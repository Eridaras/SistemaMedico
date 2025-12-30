import { NextRequest, NextResponse } from 'next/server';

// Use direct service connection (Docker internal network)
const AUTH_SERVICE_URL = process.env.AUTH_SERVICE_URL || 'http://medical_auth:5000';

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const url = `${AUTH_SERVICE_URL}/api/auth/${path}`;

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('Authorization') || '',
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Auth API Error:', error);
    return NextResponse.json(
      { success: false, message: 'Error connecting to auth service' },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const url = `${AUTH_SERVICE_URL}/api/auth/${path}`;

  try {
    const body = await request.json();

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('Authorization') || '',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Auth API Error:', error);
    return NextResponse.json(
      { success: false, message: 'Error connecting to auth service' },
      { status: 500 }
    );
  }
}
