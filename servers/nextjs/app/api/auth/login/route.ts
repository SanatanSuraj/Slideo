import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const response = await fetch(`${FASTAPI_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: body.email,
        password: body.password,
        remember_me: body.remember_me,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      // Get user info using the token
      const userResponse = await fetch(`${FASTAPI_BASE_URL}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${data.access_token}`,
        },
      });

      if (userResponse.ok) {
        const userData = await userResponse.json();
        return NextResponse.json({
          access_token: data.access_token,
          user: userData,
        });
      }
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
