import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://localhost:8004';

export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        { detail: 'Authorization header missing' },
        { status: 401 }
      );
    }

    const body = await request.json();
    
    console.log('Proxying create template request to FastAPI:', {
      url: `${FASTAPI_BASE_URL}/api/v1/ppt/template-management/templates`,
      body: body
    });

    const response = await fetch(`${FASTAPI_BASE_URL}/api/v1/ppt/template-management/templates`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader,
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    
    console.log('FastAPI response:', {
      status: response.status,
      data: data
    });

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Error proxying create template to FastAPI:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
