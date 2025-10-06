import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    
    // Debug logging
    console.log('🔍 Presentation Stream API: Request received for ID:', id);
    console.log('🔍 Presentation Stream API: Request URL:', request.url);
    console.log('🔍 Presentation Stream API: Headers:', Object.fromEntries(request.headers.entries()));
    
    // Try to get token from Authorization header first
    let token = request.headers.get('authorization');
    console.log('🔍 Presentation Stream API: Authorization header:', token ? `${token.substring(0, 20)}...` : 'None');
    
    // If no header, try to get token from query parameter (for EventSource)
    if (!token) {
      const url = new URL(request.url);
      const queryToken = url.searchParams.get('token');
      console.log('🔍 Presentation Stream API: Query token:', queryToken ? `${queryToken.substring(0, 20)}...` : 'None');
      
      if (queryToken && !queryToken.startsWith('Bearer ')) {
        token = `Bearer ${queryToken}`;
      } else if (queryToken) {
        token = queryToken;
      }
    }
    
    console.log('🔍 Presentation Stream API: Final token:', token ? `${token.substring(0, 20)}...` : 'None');
    
    if (!token || !token.startsWith('Bearer ')) {
      console.log('❌ Presentation Stream API: No valid token found');
      return NextResponse.json(
        { detail: 'Authorization token missing' },
        { status: 401 }
      );
    }

    console.log('Proxying presentation stream request to FastAPI:', {
      url: `${FASTAPI_BASE_URL}/api/v1/ppt/presentation/stream/${id}`
    });

    const response = await fetch(`${FASTAPI_BASE_URL}/api/v1/ppt/presentation/stream/${id}`, {
      method: 'GET',
      headers: {
        'Authorization': token,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('FastAPI error response:', {
        status: response.status,
        data: errorData
      });
      return NextResponse.json(errorData, { status: response.status });
    }

    // Check if response is empty (presentation not prepared)
    if (response.headers.get('content-length') === '0' || 
        response.headers.get('content-length') === null) {
      console.log('Presentation not prepared, returning error');
      return NextResponse.json(
        { detail: 'Presentation not prepared for streaming. Please complete the outline and preparation steps first.' },
        { status: 400 }
      );
    }

    // For streaming responses, we need to pass through the stream
    const stream = new ReadableStream({
      start(controller) {
        const reader = response.body?.getReader();
        
        function pump(): Promise<void> {
          return reader!.read().then(({ done, value }) => {
            if (done) {
              controller.close();
              return;
            }
            controller.enqueue(value);
            return pump();
          });
        }
        
        return pump();
      }
    });

    return new NextResponse(stream, {
      status: response.status,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  } catch (error) {
    console.error('Error proxying presentation stream to FastAPI:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
