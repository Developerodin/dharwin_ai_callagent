import { NextResponse } from 'next/server'
import { getFlaskBackendUrlServer } from '@/lib/config'

export async function GET(
  request: Request,
  { params }: { params: { executionId: string } }
) {
  try {
    const { executionId } = params

    // Call Flask backend to get execution details from Bolna AI
    // Use config helper to get backend URL (checks env vars and auto-detects from request)
    const flaskBackendUrl = getFlaskBackendUrlServer(request)
    console.log(`[API /api/call-status] Using Flask backend: ${flaskBackendUrl}`)
    
    try {
      const flaskResponse = await fetch(`${flaskBackendUrl}/api/call-status/${executionId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      })

      if (flaskResponse.ok) {
        const flaskData = await flaskResponse.json()
        if (flaskData.success) {
          return NextResponse.json({
            success: true,
            details: flaskData.details,
          })
        } else {
          throw new Error(flaskData.error || 'Flask backend returned error')
        }
      } else {
        const errorData = await flaskResponse.json().catch(() => ({}))
        throw new Error(errorData.error || `Flask backend error: ${flaskResponse.status}`)
      }
    } catch (error) {
      console.error('Error calling Flask backend:', error)
      // Fallback to basic status if Flask backend is not available
      return NextResponse.json({
        success: true,
        details: {
          executionId,
          status: 'unknown',
          error: `Could not fetch status: ${error instanceof Error ? error.message : 'Unknown error'}`,
        },
      })
    }
  } catch (error) {
    console.error('Error fetching call status:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to fetch call status' },
      { status: 500 }
    )
  }
}

