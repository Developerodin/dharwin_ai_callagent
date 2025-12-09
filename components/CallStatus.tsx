'use client'

import { useState, useEffect } from 'react'

interface CallStatusProps {
  status: {
    candidate: string
    candidateId?: number
    executionId?: string
    status: string
  }
  onClose: () => void
  onRefresh?: () => void
}

export default function CallStatus({ status, onClose, onRefresh }: CallStatusProps) {
  const [callDetails, setCallDetails] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (status.executionId) {
      // Poll for call status updates
      const interval = setInterval(async () => {
        try {
          setLoading(true)
          const response = await fetch(`/api/call-status/${status.executionId}`)
          const data = await response.json()
          
          if (data.success && data.details) {
            setCallDetails(data.details)
            
            const callStatus = data.details.status?.toLowerCase() || ''
            
            // If call is completed or ended with no answer, stop polling and refresh candidate list
            if (callStatus === 'completed' || callStatus === 'ended' || callStatus === 'stopped' || 
                callStatus === 'no_answer' || callStatus === 'no-answer' || callStatus === 'no answer') {
              clearInterval(interval)
              
              // Show outcome if available
              if (data.details.parsed_outcome) {
                const outcome = data.details.parsed_outcome
                console.log('Call outcome:', outcome)
              }
              
              // Trigger refresh immediately
              if (onRefresh) {
                onRefresh()
              }
              onClose() // This will trigger refresh in parent
              
              // Force refresh after delays to catch backend updates
              setTimeout(() => {
                if (onRefresh) onRefresh()
              }, 2000)
              setTimeout(() => {
                if (onRefresh) onRefresh()
              }, 5000)
            }
          }
        } catch (error) {
          console.error('Error fetching call status:', error)
        } finally {
          setLoading(false)
        }
      }, 5000) // Poll every 5 seconds

      return () => clearInterval(interval)
    }
  }, [status.executionId])

  return (
    <div className="card" style={{ 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      marginBottom: '1.5rem',
      position: 'relative'
    }}>
      <button
        onClick={onClose}
        style={{
          position: 'absolute',
          top: '1rem',
          right: '1rem',
          background: 'rgba(255, 255, 255, 0.2)',
          border: 'none',
          borderRadius: '50%',
          width: '32px',
          height: '32px',
          color: 'white',
          cursor: 'pointer',
          fontSize: '1.2rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        ×
      </button>
      
      <h2 style={{ marginBottom: '1rem', fontSize: '1.5rem' }}>
        📞 Call Status
      </h2>
      
      <div style={{ marginBottom: '1rem' }}>
        <strong>Candidate:</strong> {status.candidate}
      </div>
      
      {status.executionId && (
        <div style={{ marginBottom: '1rem', fontSize: '0.9rem', opacity: 0.9 }}>
          Execution ID: {status.executionId}
        </div>
      )}
      
      <div style={{ 
        background: 'rgba(255, 255, 255, 0.2)', 
        padding: '1rem', 
        borderRadius: '8px',
        marginTop: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {loading && <div className="loading"></div>}
          <span>
            {status.status === 'initiated' ? 'Call initiated...' : 'Call in progress...'}
          </span>
        </div>
      </div>
      
      {callDetails && (
        <div style={{ 
          marginTop: '1rem',
          padding: '1rem',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '8px',
          fontSize: '0.9rem'
        }}>
          <div>
            <strong>Status:</strong> {
              callDetails.status === 'no_answer' || callDetails.status === 'no-answer' || callDetails.status === 'no answer'
                ? '📵 No Answer'
                : callDetails.status || 'Active'
            }
          </div>
          {callDetails.duration && (
            <div style={{ marginTop: '0.5rem' }}>
              <strong>Duration:</strong> {callDetails.duration}
            </div>
          )}
          {(callDetails.status === 'no_answer' || callDetails.status === 'no-answer' || callDetails.status === 'no answer') && (
            <div style={{ marginTop: '0.5rem', padding: '0.5rem', background: 'rgba(255, 244, 230, 0.3)', borderRadius: '4px', color: '#b45309' }}>
              📵 The call was not answered by the candidate.
            </div>
          )}
          {callDetails.parsed_outcome && (
            <div style={{ marginTop: '0.5rem', padding: '0.5rem', background: 'rgba(255, 255, 255, 0.2)', borderRadius: '4px' }}>
              <strong>Outcome:</strong> {callDetails.parsed_outcome.status}
              {callDetails.parsed_outcome.status === 'rescheduled' && callDetails.parsed_outcome.updated_interview && (
                <div style={{ marginTop: '0.25rem', fontSize: '0.85rem' }}>
                  New slot: {callDetails.parsed_outcome.updated_interview.datetime}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

