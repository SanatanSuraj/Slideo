/**
 * Custom streaming client that replaces EventSource with fetch-based streaming
 * This allows us to send proper Authorization headers and handle authentication correctly
 */

export interface StreamingEvent {
  event?: string;
  data: string;
  id?: string;
}

export interface StreamingClientOptions {
  onMessage?: (event: StreamingEvent) => void;
  onError?: (error: Error) => void;
  onOpen?: () => void;
  onClose?: () => void;
  headers?: Record<string, string>;
  timeout?: number;
}

export class StreamingClient {
  private controller: AbortController | null = null;
  private reader: ReadableStreamDefaultReader<Uint8Array> | null = null;
  private options: StreamingClientOptions;
  private url: string;
  private isConnected = false;

  constructor(url: string, options: StreamingClientOptions = {}) {
    this.url = url;
    this.options = {
      timeout: 60000, // 60 seconds default
      ...options,
    };
  }

  async connect(): Promise<void> {
    if (this.isConnected) {
      this.disconnect();
    }

    this.controller = new AbortController();
    
    try {
      console.log('🔍 StreamingClient: Connecting to:', this.url);
      console.log('🔍 StreamingClient: Headers:', this.options.headers);

      const response = await fetch(this.url, {
        method: 'GET',
        headers: {
          'Accept': 'text/event-stream',
          'Cache-Control': 'no-cache',
          ...this.options.headers,
        },
        signal: this.controller.signal,
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('🔍 StreamingClient: Response not OK:', response.status, errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      this.isConnected = true;
      this.options.onOpen?.();
      console.log('🔍 StreamingClient: Connection opened successfully');

      // Set up timeout
      const timeoutId = setTimeout(() => {
        console.log('🔍 StreamingClient: Connection timeout');
        this.disconnect();
        this.options.onError?.(new Error('Connection timeout'));
      }, this.options.timeout);

      this.reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      try {
        while (true) {
          const { done, value } = await this.reader.read();
          
          if (done) {
            console.log('🔍 StreamingClient: Stream ended');
            break;
          }

          // Clear timeout on successful read
          clearTimeout(timeoutId);

          buffer += decoder.decode(value, { stream: true });
          
          // Process complete events
          const events = this.parseSSEEvents(buffer);
          for (const event of events.complete) {
            console.log('🔍 StreamingClient: Received event:', event);
            this.options.onMessage?.(event);
          }
          
          buffer = events.remaining;
        }
      } catch (error) {
        if ((error as any).name !== 'AbortError') {
          console.error('🔍 StreamingClient: Read error:', error);
          this.options.onError?.(error as Error);
        }
      } finally {
        clearTimeout(timeoutId);
        this.disconnect();
      }

    } catch (error) {
      console.error('🔍 StreamingClient: Connection error:', error);
      this.isConnected = false;
      this.options.onError?.(error as Error);
    }
  }

  private parseSSEEvents(buffer: string): { complete: StreamingEvent[], remaining: string } {
    const events: StreamingEvent[] = [];
    const lines = buffer.split('\n');
    let currentEvent: Partial<StreamingEvent> = {};
    let i = 0;

    while (i < lines.length) {
      const line = lines[i];
      
      if (line === '') {
        // Empty line indicates end of event
        if (currentEvent.data !== undefined) {
          events.push({
            event: currentEvent.event,
            data: currentEvent.data,
            id: currentEvent.id,
          });
        }
        currentEvent = {};
        i++;
        continue;
      }

      if (line.startsWith('data: ')) {
        currentEvent.data = line.substring(6);
      } else if (line.startsWith('event: ')) {
        currentEvent.event = line.substring(7);
      } else if (line.startsWith('id: ')) {
        currentEvent.id = line.substring(4);
      }
      
      i++;
    }

    // Find the last complete event boundary
    let lastCompleteIndex = buffer.lastIndexOf('\n\n');
    if (lastCompleteIndex === -1) {
      lastCompleteIndex = buffer.lastIndexOf('\n');
    }
    
    const remaining = lastCompleteIndex === -1 ? buffer : buffer.substring(lastCompleteIndex + 1);
    
    return { complete: events, remaining };
  }

  disconnect(): void {
    console.log('🔍 StreamingClient: Disconnecting');
    
    if (this.controller) {
      this.controller.abort();
      this.controller = null;
    }
    
    if (this.reader) {
      this.reader.cancel();
      this.reader = null;
    }
    
    if (this.isConnected) {
      this.isConnected = false;
      this.options.onClose?.();
    }
  }

  get connected(): boolean {
    return this.isConnected;
  }
}
