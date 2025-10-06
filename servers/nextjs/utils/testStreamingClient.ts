/**
 * Simple test utility to verify the streaming client works
 * This can be run in the browser console for debugging
 */

import { StreamingClient } from './streamingClient';

export const testStreamingClient = async (url: string, token: string) => {
  console.log('🧪 Testing StreamingClient with URL:', url);
  
  const client = new StreamingClient(url, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    onOpen: () => {
      console.log('✅ Test: Connection opened');
    },
    onMessage: (event) => {
      console.log('📨 Test: Message received:', event);
    },
    onError: (error) => {
      console.error('❌ Test: Error occurred:', error);
    },
    onClose: () => {
      console.log('🔒 Test: Connection closed');
    }
  });

  try {
    await client.connect();
  } catch (error) {
    console.error('❌ Test: Failed to connect:', error);
  }

  // Auto-disconnect after 30 seconds for testing
  setTimeout(() => {
    console.log('⏰ Test: Auto-disconnecting after 30 seconds');
    client.disconnect();
  }, 30000);

  return client;
};

// Make it available globally for browser console testing
if (typeof window !== 'undefined') {
  (window as any).testStreamingClient = testStreamingClient;
}
