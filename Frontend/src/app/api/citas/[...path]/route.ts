import { NextRequest, NextResponse } from 'next/server';

const SERVICE_URL = process.env.CITAS_SERVICE_URL || 'http://medical_citas:5000';

async function handleRequest(
  request: NextRequest,
  params: { path: string[] },
  method: string
) {
  const path = params.path.join('/');
  const url = `${SERVICE_URL}/api/citas/${path}${request.nextUrl.search}`;

  try {
    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('Authorization') || '',
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
    console.error('Citas API Error:', error);
    return NextResponse.json(
      { success: false, message: 'Error connecting to citas service' },
      { status: 500 }
    );
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return handleRequest(request, params, 'GET');
}

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return handleRequest(request, params, 'POST');
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return handleRequest(request, params, 'PUT');
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return handleRequest(request, params, 'DELETE');
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return handleRequest(request, params, 'PATCH');
}
