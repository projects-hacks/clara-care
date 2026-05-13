import { NextRequest, NextResponse } from 'next/server'

// Port 5001 avoids conflict with macOS Control Center (AirPlay) on 5000
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5001'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path?: string[] }> }
) {
  return proxy(request, params)
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path?: string[] }> }
) {
  return proxy(request, params)
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path?: string[] }> }
) {
  return proxy(request, params)
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path?: string[] }> }
) {
  return proxy(request, params)
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path?: string[] }> }
) {
  return proxy(request, params)
}

async function proxy(
  request: NextRequest,
  params: Promise<{ path?: string[] }>
) {
  const { path } = await params
  const pathSegments = path && path.length > 0 ? path.join('/') : ''
  const search = request.nextUrl.search
  const url = `${BACKEND_URL}/api/${pathSegments}${search}`
  const backendHost = new URL(BACKEND_URL).host

  try {
    // Forward Accept header from original request (important for PDF downloads)
    const acceptHeader = request.headers.get('Accept') || 'application/json'
    
    const res = await fetch(url, {
      method: request.method,
      headers: {
        'Content-Type': 'application/json',
        Accept: acceptHeader,
        Host: backendHost,
        'User-Agent': 'ClaraCare-Dashboard/1.0',
      },
      cache: 'no-store',
      signal: AbortSignal.timeout(30000), // 30 second timeout
      ...(request.method !== 'GET' && request.body && {
        body: await request.text(),
      }),
    })

    if (process.env.NODE_ENV === 'development' && !res.ok) {
      console.warn(`[backend-api] ${res.status} ${request.method} ${url}`)
    }

    const contentType = res.headers.get('content-type')
    const isJson = contentType?.includes('application/json')
    const isBinary = contentType?.includes('application/pdf') || contentType?.includes('application/octet-stream')

    if (isJson) {
      const data = await res.json().catch(() => ({}))
      return NextResponse.json(data, { status: res.status })
    }

    // Handle binary data (PDFs) properly
    if (isBinary) {
      const arrayBuffer = await res.arrayBuffer()
      return new NextResponse(arrayBuffer, {
        status: res.status,
        headers: { 
          'Content-Type': contentType || 'application/octet-stream',
          'Content-Disposition': res.headers.get('Content-Disposition') || '',
        },
      })
    }

    const text = await res.text()
    return new NextResponse(text, {
      status: res.status,
      headers: { 'Content-Type': contentType || 'text/plain' },
    })
  } catch (err) {
    console.error('[backend-api proxy]', url, err)
    return NextResponse.json(
      { error: 'Backend unreachable', detail: String(err) },
      { status: 502 }
    )
  }
}
