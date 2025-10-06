import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://localhost:8004';

export async function PATCH(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        { detail: 'Authorization header missing' },
        { status: 401 }
      );
    }

    const body = await request.json();

    console.log('Proxying presentation update request to FastAPI:', {
      url: `${FASTAPI_BASE_URL}/api/v1/ppt/presentation/update`,
      body,
    });

    const response = await fetch(`${FASTAPI_BASE_URL}/api/v1/ppt/presentation/update`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader,
      },
      body: JSON.stringify(body),
    });

    const text = await response.text();
    let data;

    try {
      data = text ? JSON.parse(text) : null;
    } catch (error) {
      console.error('Error parsing FastAPI response JSON:', error, 'Raw response:', text);
      return NextResponse.json(
        { detail: 'Invalid response from server' },
        { status: 500 }
      );
    }

    console.log('FastAPI response:', {
      status: response.status,
      data,
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
