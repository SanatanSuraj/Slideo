import { NextResponse } from 'next/server';

export async function POST() {
  // For JWT tokens, logout is typically handled client-side by removing the token
  // The server doesn't need to do anything special since JWT tokens are stateless
  return NextResponse.json({ message: 'Logged out successfully' });
}
