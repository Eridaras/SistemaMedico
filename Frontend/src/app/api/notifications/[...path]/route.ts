import { NextRequest, NextResponse } from 'next/server';

const SERVICE_URL = process.env.NOTIFICATIONS_SERVICE_URL || 'http://medical_notifications:5000';

async function handleRequest(
  request: NextRequest,
  pathArray: string[],
  method: string
) {
  const path = pathArray.join('/');
  const url = `${SERVICE_URL}/api/notifications/${path}${request.nextUrl.search}`;

  try {
    // Get Authorization header from request - check both cases
    const authHeader = request.headers.get('Authorization') || request.headers.get('authorization') || '';

    // Log for debugging (remove in production)
    if (!authHeader) {
      console.warn('No Authorization header found in request to:', url);
    }

    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader && { 'Authorization': authHeader }),
      },
    };

    if (method !== 'GET' && method !== 'HEAD') {
      const body = await request.text();
      if (body) options.body = body;
    }

    const response = await fetch(url, options);
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Notifications API Error:', error);
    return NextResponse.json(
      { success: false, message: 'Error connecting to notifications service' },
      { status: 500 }
    );
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return handleRequest(request, path, 'GET');
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return handleRequest(request, path, 'POST');
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return handleRequest(request, path, 'PUT');
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return handleRequest(request, path, 'DELETE');
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return handleRequest(request, path, 'PATCH');
}
