import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://localhost:8004';

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        { detail: 'Authorization header missing' },
        { status: 401 }
      );
    }

    console.log('Proxying template management summary request to FastAPI:', {
      url: `${FASTAPI_BASE_URL}/api/v1/ppt/template-management/summary`
    });

    const response = await fetch(`${FASTAPI_BASE_URL}/api/v1/ppt/template-management/summary`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
      },
    });

    const data = await response.json();
    
    console.log('FastAPI response:', {
      status: response.status,
      data: data
    });

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Error proxying template management summary to FastAPI:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
