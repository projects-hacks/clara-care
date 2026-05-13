import { NextResponse } from 'next/server'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const patientId = searchParams.get('patient_id')

  if (!patientId) {
    return NextResponse.json(
      { error: 'patient_id is required' },
      { status: 400 }
    )
  }

  try {
    const res = await fetch(`${API_URL}/api/live-status?patient_id=${patientId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    })

    if (!res.ok) {
      console.error(`[Dashboard API] Live status failed: ${res.status}`)
      return NextResponse.json(
        { is_active: false, error: 'Failed to fetch call status' },
        { status: res.status }
      )
    }

    const data = await res.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('[Dashboard API] Live status network error:', error)
    return NextResponse.json(
      { is_active: false, error: 'Network error' },
      { status: 500 }
    )
  }
}
