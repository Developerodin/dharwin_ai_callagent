/**
 * Configuration utilities for API endpoints
 * Uses environment variables with fallback to localhost for local development
 * Automatically detects EC2/public IP when running on remote server
 */

/**
 * Get Flask backend URL for server-side use (Next.js API routes, SSR)
 * @param request Optional Request object to extract hostname from headers
 */
export const getFlaskBackendUrlServer = (request?: Request): string => {
  // 1. Check environment variables first
  const envUrl = process.env.FLASK_BACKEND_URL || process.env.NEXT_PUBLIC_FLASK_BACKEND_URL
  if (envUrl) {
    console.log(`[Config] Server-side using env var: ${envUrl}`)
    return envUrl
  }
  
  // 2. Try to infer from request headers (for server-side API routes)
  if (request) {
    const hostHeader = request.headers.get('host') || request.headers.get('x-forwarded-host')
    if (hostHeader) {
      const hostname = hostHeader.split(':')[0] // Remove port if present
      if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1' && !hostname.includes('localhost')) {
        const backendUrl = `http://${hostname}:5000`
        console.log(`[Config] Server-side auto-detected from headers: ${backendUrl}`)
        return backendUrl
      }
    }
  }
  
  // 3. Fallback to localhost for local development
  console.log(`[Config] Server-side falling back to localhost:5000`)
  return 'http://localhost:5000'
}

/**
 * Get Flask backend URL for client-side use (browser)
 */
export const getFlaskBackendUrl = (): string => {
  // In browser/client-side
  if (typeof window !== 'undefined') {
    // 1. Check environment variable FIRST (explicit configuration takes priority)
    const envUrl = process.env.NEXT_PUBLIC_FLASK_BACKEND_URL
    if (envUrl) {
      console.log(`[Config] Using NEXT_PUBLIC_FLASK_BACKEND_URL: ${envUrl}`)
      return envUrl
    }
    
    // 2. Auto-detect from current hostname (works at runtime)
    const hostname = window.location.hostname
    const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:'
    
    // If we're not on localhost, use current hostname for backend
    if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1' && !hostname.includes('localhost')) {
      // Use same hostname but port 5000 for Flask backend
      const backendUrl = `http://${hostname}:5000`
      console.log(`[Config] Auto-detected backend URL: ${backendUrl}`)
      return backendUrl
    }
    
    // 3. Fallback to localhost for local development
    console.log(`[Config] Falling back to localhost:5000`)
    return 'http://localhost:5000'
  }
  
  // Server-side (SSR): use server helper function
  return getFlaskBackendUrlServer()
}

