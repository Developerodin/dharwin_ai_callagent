import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

// Force dynamic rendering for this API route
export const dynamic = 'force-dynamic'

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const excludeDatetime = searchParams.get('exclude')

    const filePath = path.join(process.cwd(), 'data', 'candidates.json')
    const fileContents = fs.readFileSync(filePath, 'utf8')
    const data = JSON.parse(fileContents)

    let slots = data.availableSlots

    // Exclude a specific datetime if provided
    if (excludeDatetime) {
      slots = slots.filter(
        (slot: any) => slot.datetime !== excludeDatetime
      )
    }

    return NextResponse.json({
      success: true,
      slots,
    })
  } catch (error) {
    console.error('Error fetching available slots:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to fetch available slots' },
      { status: 500 }
    )
  }
}

