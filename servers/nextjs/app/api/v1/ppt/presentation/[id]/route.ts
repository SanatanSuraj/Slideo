import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://localhost:8004';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const authHeader = request.headers.get('authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        { detail: 'Authorization header missing' },
        { status: 401 }
      );
    }

    const { id } = params;

    console.log('Proxying get presentation request to FastAPI:', {
      url: `${FASTAPI_BASE_URL}/api/v1/ppt/presentation/${id}`
    });

    const response = await fetch(`${FASTAPI_BASE_URL}/api/v1/ppt/presentation/${id}`, {
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
    console.error('Error proxying to FastAPI:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const authHeader = request.headers.get('authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        { detail: 'Authorization header missing' },
        { status: 401 }
      );
    }

    const { id } = params;

    console.log('Proxying delete presentation request to FastAPI:', {
      url: `${FASTAPI_BASE_URL}/api/v1/ppt/presentation/${id}`
    });

    const response = await fetch(`${FASTAPI_BASE_URL}/api/v1/ppt/presentation/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': authHeader,
      },
    });

    console.log('FastAPI response:', {
      status: response.status
    });

    return new NextResponse(null, { status: response.status });
  } catch (error) {
    console.error('Error proxying to FastAPI:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
