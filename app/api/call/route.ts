import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { candidateId, phone, name, interviewDate, interviewTime } = body

    // Read candidates and available slots
    const filePath = path.join(process.cwd(), 'data', 'candidates.json')
    const fileContents = fs.readFileSync(filePath, 'utf8')
    const data = JSON.parse(fileContents)

    // Find the candidate
    const candidate = data.candidates.find((c: any) => c.id === candidateId)
    if (!candidate) {
      return NextResponse.json(
        { success: false, error: 'Candidate not found' },
        { status: 404 }
      )
    }

    // Get available slots for rescheduling (use candidate-specific slots if assigned)
    let alternativeSlots: string[] = []
    
    if (candidate.reschedulingSlots && candidate.reschedulingSlots.length > 0) {
      // Use candidate-specific rescheduling slots
      const slotIds = candidate.reschedulingSlots as number[]
      const slotMap = new Map(
        data.availableSlots.map((slot: any) => [slot.id, slot])
      )
      
      alternativeSlots = slotIds
        .filter((slotId: number) => {
          const slot = slotMap.get(slotId)
          return slot && slot.datetime !== candidate.scheduledInterview.datetime
        })
        .map((slotId: number) => slotMap.get(slotId).datetime)
    } else {
      // Fallback: Use all available slots (excluding current)
      alternativeSlots = data.availableSlots
        .filter((slot: any) => 
          slot.datetime !== candidate.scheduledInterview.datetime
        )
        .slice(0, 3) // Limit to 3 alternative slots
        .map((slot: any) => slot.datetime)
    }

    // Call Flask backend to make actual Bolna AI call
    let executionId: string
    const flaskBackendUrl = process.env.NEXT_PUBLIC_FLASK_BACKEND_URL || 'http://localhost:5000'
    
    try {
      // Call Flask backend which connects to Bolna AI
      const flaskResponse = await fetch(`${flaskBackendUrl}/api/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidateId,
          phone,
          name,
          interviewDate,
          interviewTime,
        }),
      })

      if (flaskResponse.ok) {
        const flaskData = await flaskResponse.json()
        if (flaskData.success) {
          executionId = flaskData.executionId
        } else {
          throw new Error(flaskData.error || 'Flask backend returned error')
        }
      } else {
        const errorData = await flaskResponse.json().catch(() => ({}))
        throw new Error(errorData.error || `Flask backend error: ${flaskResponse.status}`)
      }
    } catch (error) {
      console.error('Error calling Flask backend:', error)
      // Return error instead of falling back to mock
      return NextResponse.json(
        { 
          success: false, 
          error: `Failed to initiate call: ${error instanceof Error ? error.message : 'Unknown error'}. Make sure Flask backend is running on ${flaskBackendUrl}` 
        },
        { status: 500 }
      )
    }
    
    // Only update candidate status to 'calling' if call was successfully initiated
    if (executionId) {
      candidate.status = 'calling'
      // Write back to file
      fs.writeFileSync(filePath, JSON.stringify(data, null, 2))
    }

    return NextResponse.json({
      success: true,
      executionId,
      message: 'Call initiated successfully',
      alternativeSlots, // Send available slots for rescheduling
    })
  } catch (error) {
    console.error('Error initiating call:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to initiate call' },
      { status: 500 }
    )
  }
}

