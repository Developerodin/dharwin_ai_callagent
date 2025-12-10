import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

// Force dynamic rendering to prevent caching
export const dynamic = 'force-dynamic'
export const revalidate = 0

export async function GET(request: Request) {
  try {
    const filePath = path.join(process.cwd(), 'data', 'candidates.json')
    
    // Log file path and stats for debugging
    const fileStats = fs.statSync(filePath)
    console.log(`[Next.js API] Reading candidates from: ${filePath}`)
    console.log(`[Next.js API] File last modified: ${fileStats.mtime.toISOString()}`)
    
    const fileContents = fs.readFileSync(filePath, 'utf8')
    const data = JSON.parse(fileContents)
    
    // Log status breakdown
    const statusCounts = (data.candidates || []).reduce((acc: any, c: any) => {
      acc[c.status] = (acc[c.status] || 0) + 1;
      return acc;
    }, {});
    console.log(`[Next.js API] Status counts:`, statusCounts)
    
    // Add cache control headers to prevent caching
    return NextResponse.json(data, {
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      }
    })
  } catch (error) {
    console.error('[Next.js API] Error reading candidates:', error)
    return NextResponse.json(
      { error: 'Failed to fetch candidates' },
      { status: 500 }
    )
  }
}

