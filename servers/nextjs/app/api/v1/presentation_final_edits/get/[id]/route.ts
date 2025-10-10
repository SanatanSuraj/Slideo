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
    
    // Get token from Authorization header
    let token = request.headers.get('authorization');
    
    // If no header, try to get token from query parameter
    if (!token) {
      const url = new URL(request.url);
      const queryToken = url.searchParams.get('token');
      
      if (queryToken && !queryToken.startsWith('Bearer ')) {
        token = `Bearer ${queryToken}`;
      } else if (queryToken) {
        token = queryToken;
      }
    }
    
    if (!token || !token.startsWith('Bearer ')) {
      return NextResponse.json(
        { detail: 'Authorization token missing' },
        { status: 401 }
      );
    }

    const response = await fetch(`${FASTAPI_BASE_URL}/api/v1/presentation_final_edits/get/${id}`, {
      method: 'GET',
      headers: {
        'Authorization': token,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(errorData, { 
        status: response.status,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
      });
    }

    const data = await response.json();
    return NextResponse.json(data, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    });
  } catch (error) {
    console.error('Error getting presentation final edit data:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
