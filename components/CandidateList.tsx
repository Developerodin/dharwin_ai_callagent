'use client'

import { useState } from 'react'
import CandidateCard from './CandidateCard'
import ManageReschedulingSlotsModal from './ManageReschedulingSlotsModal'
import { getFlaskBackendUrl } from '@/lib/config'

interface Candidate {
  id: number
  name: string
  phone: string
  email: string
  position: string
  status: string
  scheduledInterview: {
    date: string
    time: string
    day: string
    datetime: string
  }
  originalInterview?: {
    date: string
    time: string
    day: string
    datetime: string
  }
  reschedulingSlots?: number[]
  applicationDate: string
}

interface CandidateListProps {
  candidates: Candidate[]
  availableSlots: any[]
  onCallInitiated: (status: any) => void
  onStatusUpdate: () => void
}

export default function CandidateList({ 
  candidates,
  availableSlots,
  onCallInitiated, 
  onStatusUpdate 
}: CandidateListProps) {
  const [callingId, setCallingId] = useState<number | null>(null)
  const [manageSlotsCandidate, setManageSlotsCandidate] = useState<{ id: number; name: string; slots: number[] } | null>(null)

  const handleCall = async (candidate: Candidate) => {
    setCallingId(candidate.id)
    
    try {
      const response = await fetch('/api/call', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          candidateId: candidate.id,
          phone: candidate.phone,
          name: candidate.name,
          interviewDate: candidate.scheduledInterview.date,
          interviewTime: candidate.scheduledInterview.time,
        }),
      })

      const data = await response.json()
      
      if (data.success) {
        onCallInitiated({
          candidate: candidate.name,
          candidateId: candidate.id,
          executionId: data.executionId,
          status: 'initiated',
        })
        // Trigger refresh after call is initiated
        setTimeout(() => {
          onStatusUpdate()
        }, 2000)
      } else {
        alert(`Error: ${data.error || 'Failed to initiate call'}`)
      }
    } catch (error) {
      console.error('Error making call:', error)
      alert('Failed to initiate call. Please try again.')
    } finally {
      setCallingId(null)
    }
  }

  const handleReset = async (candidateId: number) => {
    if (!confirm('Are you sure you want to reset this candidate\'s status to pending?')) {
      return
    }

    try {
      const backendUrl = getFlaskBackendUrl()
      const response = await fetch(`${backendUrl}/api/candidate/${candidateId}/reset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      const data = await response.json()
      
      if (data.success) {
        alert('Candidate status reset to pending!')
        
        // Wait a bit to ensure Flask has written the file, then refresh
        setTimeout(() => {
          onStatusUpdate()
        }, 500);
        
        // Also refresh after a longer delay as backup
        setTimeout(() => {
          onStatusUpdate()
        }, 1500);
      } else {
        alert(`Error: ${data.error || 'Failed to reset candidate'}`)
      }
    } catch (error) {
      console.error('Error resetting candidate:', error)
      alert('Failed to reset candidate. Please try again.')
    }
  }

  const handleDelete = async (candidateId: number) => {
    if (!confirm('Are you sure you want to permanently delete this candidate? This action cannot be undone.')) {
      return
    }

    try {
      const backendUrl = getFlaskBackendUrl()
      const response = await fetch(`${backendUrl}/api/candidate/${candidateId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      const data = await response.json()
      
      if (data.success) {
        alert('Candidate deleted successfully!')
        onStatusUpdate()
      } else {
        alert(`Error: ${data.error || 'Failed to delete candidate'}`)
      }
    } catch (error) {
      console.error('Error deleting candidate:', error)
      alert('Failed to delete candidate. Please try again.')
    }
  }

  if (candidates.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
        <p>No candidates found.</p>
      </div>
    )
  }

  return (
    <>
      <div>
        {candidates.map((candidate) => (
          <CandidateCard
            key={candidate.id}
            candidate={candidate}
            onCall={() => handleCall(candidate)}
            isCalling={callingId === candidate.id}
            onReset={() => handleReset(candidate.id)}
            onDelete={() => handleDelete(candidate.id)}
            onManageSlots={() => setManageSlotsCandidate({
              id: candidate.id,
              name: candidate.name,
              slots: candidate.reschedulingSlots || []
            })}
          />
        ))}
      </div>

      {manageSlotsCandidate && (
        <ManageReschedulingSlotsModal
          isOpen={!!manageSlotsCandidate}
          onClose={() => setManageSlotsCandidate(null)}
          onSuccess={() => {
            onStatusUpdate()
            setManageSlotsCandidate(null)
          }}
          candidateId={manageSlotsCandidate.id}
          candidateName={manageSlotsCandidate.name}
          availableSlots={availableSlots}
          currentReschedulingSlots={manageSlotsCandidate.slots}
        />
      )}
    </>
  )
}
