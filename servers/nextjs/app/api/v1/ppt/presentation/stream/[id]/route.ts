import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://localhost:8000';

export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}

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
        data: errorData,
        url: `${FASTAPI_BASE_URL}/api/v1/ppt/presentation/stream/${id}`
      });
      return NextResponse.json(errorData, { 
        status: response.status,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
      });
    }

    // Note: Streaming responses use transfer-encoding: chunked and don't have content-length
    // The FastAPI endpoint will return appropriate error status codes if presentation isn't prepared

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
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
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
