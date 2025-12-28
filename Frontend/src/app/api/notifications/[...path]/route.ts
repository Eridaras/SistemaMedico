import { NextRequest, NextResponse } from 'next/server';

const NOTIFICATIONS_SERVICE_URL = process.env.NOTIFICATIONS_SERVICE_URL || 'http://localhost:5007/api/notifications';

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const searchParams = request.nextUrl.searchParams.toString();
  const url = `${NOTIFICATIONS_SERVICE_URL}/${path}${searchParams ? `?${searchParams}` : ''}`;

  const token = request.headers.get('authorization');

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': token }),
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Notifications service error:', error);
    return NextResponse.json(
      { success: false, message: 'Service unavailable' },
      { status: 503 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const url = `${NOTIFICATIONS_SERVICE_URL}/${path}`;

  const token = request.headers.get('authorization');
  const body = await request.json();

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': token }),
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Notifications service error:', error);
    return NextResponse.json(
      { success: false, message: 'Service unavailable' },
      { status: 503 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const url = `${NOTIFICATIONS_SERVICE_URL}/${path}`;

  const token = request.headers.get('authorization');
  const body = await request.json();

  try {
    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': token }),
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Notifications service error:', error);
    return NextResponse.json(
      { success: false, message: 'Service unavailable' },
      { status: 503 }
    );
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const url = `${NOTIFICATIONS_SERVICE_URL}/${path}`;

  const token = request.headers.get('authorization');
  const body = await request.json().catch(() => ({}));

  try {
    const response = await fetch(url, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': token }),
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Notifications service error:', error);
    return NextResponse.json(
      { success: false, message: 'Service unavailable' },
      { status: 503 }
    );
  }
}
