import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://localhost:8004';

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

    console.log('Proxying delete template request to FastAPI:', {
      url: `${FASTAPI_BASE_URL}/api/v1/ppt/template-management/delete-templates/${id}`
    });

    const response = await fetch(`${FASTAPI_BASE_URL}/api/v1/ppt/template-management/delete-templates/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': authHeader,
      },
    });

    if (response.status === 204) {
      return new NextResponse(null, { status: 204 });
    }

    const data = await response.json();
    
    console.log('FastAPI response:', {
      status: response.status,
      data: data
    });

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Error proxying delete template to FastAPI:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
