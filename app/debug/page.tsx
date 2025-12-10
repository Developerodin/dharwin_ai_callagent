'use client'

import { useState, useEffect } from 'react'
import { getFlaskBackendUrl } from '@/lib/config'

export default function DebugPage() {
  const [backendUrl, setBackendUrl] = useState<string>('')
  const [testResult, setTestResult] = useState<string>('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setBackendUrl(getFlaskBackendUrl())
  }, [])

  const testBackend = async () => {
    setLoading(true)
    setTestResult('Testing...')
    
    try {
      const url = getFlaskBackendUrl()
      console.log('Testing backend URL:', url)
      
      const response = await fetch(`${url}/api/candidates`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setTestResult(`✅ SUCCESS! Backend is reachable at ${url}\n\nResponse: ${JSON.stringify(data, null, 2)}`)
      } else {
        setTestResult(`⚠️ Backend responded with error: ${response.status} ${response.statusText}\n\n${JSON.stringify(data, null, 2)}`)
      }
    } catch (error: any) {
      setTestResult(`❌ FAILED to connect to backend!\n\nError: ${error.message}\n\nBackend URL tried: ${backendUrl}\n\nPossible causes:\n1. Flask backend is not running\n2. Port 5000 is blocked\n3. CORS issue\n4. Wrong URL`)
    } finally {
      setLoading(false)
    }
  }

  const testReset = async () => {
    setLoading(true)
    setTestResult('Testing reset endpoint...')
    
    try {
      const url = getFlaskBackendUrl()
      const response = await fetch(`${url}/api/reset-statuses`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      const data = await response.json()
      
      if (response.ok && data.success) {
        setTestResult(`✅ Reset endpoint works!\n\nResponse: ${JSON.stringify(data, null, 2)}`)
      } else {
        setTestResult(`⚠️ Reset endpoint returned error:\n\n${JSON.stringify(data, null, 2)}`)
      }
    } catch (error: any) {
      setTestResult(`❌ Reset endpoint FAILED!\n\nError: ${error.message}\n\nBackend URL: ${backendUrl}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Backend Connection Debug</h1>
      
      <div style={{ 
        background: '#f5f5f5', 
        padding: '1rem', 
        borderRadius: '8px', 
        marginBottom: '1rem',
        fontFamily: 'monospace'
      }}>
        <div><strong>Detected Backend URL:</strong></div>
        <div style={{ color: '#0066cc', marginTop: '0.5rem' }}>{backendUrl}</div>
        <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#666' }}>
          Environment: {typeof window !== 'undefined' ? 'Browser (Client)' : 'Server'}
        </div>
        <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#666' }}>
          Hostname: {typeof window !== 'undefined' ? window.location.hostname : 'N/A'}
        </div>
        <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#666' }}>
          ENV Variable: {process.env.NEXT_PUBLIC_FLASK_BACKEND_URL || 'Not set'}
        </div>
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <button
          onClick={testBackend}
          disabled={loading}
          className="btn btn-primary"
          style={{ minWidth: '200px' }}
        >
          {loading ? 'Testing...' : 'Test Backend Connection'}
        </button>
        
        <button
          onClick={testReset}
          disabled={loading}
          className="btn btn-secondary"
          style={{ minWidth: '200px' }}
        >
          {loading ? 'Testing...' : 'Test Reset Endpoint'}
        </button>
      </div>

      {testResult && (
        <div style={{
          background: '#fff',
          border: '1px solid #ddd',
          padding: '1rem',
          borderRadius: '8px',
          whiteSpace: 'pre-wrap',
          fontFamily: 'monospace',
          fontSize: '0.9rem',
          maxHeight: '400px',
          overflow: 'auto'
        }}>
          {testResult}
        </div>
      )}

      <div style={{ marginTop: '2rem', padding: '1rem', background: '#fff3cd', borderRadius: '8px' }}>
        <h3>Troubleshooting Steps:</h3>
        <ol>
          <li>Make sure Flask backend is running on port 5000</li>
          <li>Check if the backend URL above is correct</li>
          <li>If on EC2, verify port 5000 is open in Security Group</li>
          <li>Check browser console (F12) for CORS errors</li>
          <li>Test backend directly: <code>curl {backendUrl}/api/candidates</code></li>
        </ol>
      </div>
    </div>
  )
}

