/**
 * Configuration utilities for API endpoints
 * Uses environment variables with fallback to localhost for local development
 * Automatically detects EC2/public IP when running on remote server
 */

export const getFlaskBackendUrl = (): string => {
  // In browser/client-side - MUST check runtime hostname FIRST (before env var)
  if (typeof window !== 'undefined') {
    // Auto-detect FIRST (before env var) - this works at runtime
    const hostname = window.location.hostname
    const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:'
    
    // If we're not on localhost, use current hostname for backend
    if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1' && !hostname.includes('localhost')) {
      // Use same hostname but port 5000 for Flask backend
      const backendUrl = `http://${hostname}:5000`
      console.log(`[Config] Auto-detected backend URL: ${backendUrl}`)
      return backendUrl
    }
    
    // Try environment variable (set at build time) - only use if hostname is localhost
    const envUrl = process.env.NEXT_PUBLIC_FLASK_BACKEND_URL
    if (envUrl) {
      console.log(`[Config] Using NEXT_PUBLIC_FLASK_BACKEND_URL: ${envUrl}`)
      return envUrl
    }
    
    // Fallback to localhost for local development
    console.log(`[Config] Falling back to localhost:5000`)
    return 'http://localhost:5000'
  }
  
  // Server-side (SSR): use environment variable or fallback
  const serverEnvUrl = process.env.FLASK_BACKEND_URL || process.env.NEXT_PUBLIC_FLASK_BACKEND_URL
  if (serverEnvUrl) {
    console.log(`[Config] Server-side using env var: ${serverEnvUrl}`)
    return serverEnvUrl
  }
  console.log(`[Config] Server-side falling back to localhost:5000`)
  return 'http://localhost:5000'
}

export const FLASK_BACKEND_URL = getFlaskBackendUrl()

