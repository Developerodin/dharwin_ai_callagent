'use client'

import { useState, useEffect } from 'react'
import { getFlaskBackendUrl } from '@/lib/config'

interface AvailableSlot {
  id: number
  date: string
  time: string
  day: string
  datetime: string
}

interface ManageReschedulingSlotsModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  candidateId: number
  candidateName: string
  availableSlots: AvailableSlot[]
  currentReschedulingSlots: number[]
}

export default function ManageReschedulingSlotsModal({
  isOpen,
  onClose,
  onSuccess,
  candidateId,
  candidateName,
  availableSlots,
  currentReschedulingSlots
}: ManageReschedulingSlotsModalProps) {
  const [selectedSlots, setSelectedSlots] = useState<number[]>(currentReschedulingSlots)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setSelectedSlots(currentReschedulingSlots)
    }
  }, [isOpen, currentReschedulingSlots])

  const toggleSlot = (slotId: number) => {
    setSelectedSlots(prev => 
      prev.includes(slotId)
        ? prev.filter(id => id !== slotId)
        : [...prev, slotId]
    )
  }

  const handleSave = async () => {
    setSaving(true)
    const backendUrl = getFlaskBackendUrl()
    try {
      console.log(`[Update Slots] Calling: ${backendUrl}/api/candidate/${candidateId}/rescheduling-slots`)
      console.log(`[Update Slots] Payload:`, { reschedulingSlots: selectedSlots })
      
      const response = await fetch(`${backendUrl}/api/candidate/${candidateId}/rescheduling-slots`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          reschedulingSlots: selectedSlots
        }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error(`[Update Slots] HTTP ${response.status}:`, errorText)
        throw new Error(`HTTP ${response.status}: ${errorText || 'Server error'}`)
      }

      const data = await response.json()
      console.log('[Update Slots] Response:', data)
      
      if (data.success) {
        alert('Rescheduling slots updated successfully!')
        onSuccess()
        onClose()
      } else {
        alert(`Error: ${data.error || 'Failed to update rescheduling slots'}`)
      }
    } catch (error) {
      console.error('Error updating rescheduling slots:', error)
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      console.error('Full error details:', { error, backendUrl, candidateId, selectedSlots })
      alert(`Failed to update rescheduling slots: ${errorMessage}. Check console for details.`)
    } finally {
      setSaving(false)
    }
  }

  if (!isOpen) return null

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div className="card" style={{
        maxWidth: '500px',
        width: '90%',
        maxHeight: '90vh',
        overflowY: 'auto'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Manage Rescheduling Slots</h2>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '1.5rem',
              cursor: 'pointer',
              color: '#666'
            }}
          >
            ×
          </button>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <strong>Candidate:</strong> {candidateName}
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
            Select Rescheduling Slots (Multiple selection allowed)
          </label>
          <div style={{
            border: '1px solid #ddd',
            borderRadius: '4px',
            padding: '0.5rem',
            maxHeight: '300px',
            overflowY: 'auto'
          }}>
            {availableSlots.map(slot => (
              <label 
                key={slot.id} 
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  marginBottom: '0.5rem',
                  padding: '0.5rem',
                  backgroundColor: selectedSlots.includes(slot.id) ? '#e3f2fd' : 'transparent',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                <input
                  type="checkbox"
                  checked={selectedSlots.includes(slot.id)}
                  onChange={() => toggleSlot(slot.id)}
                  style={{ marginRight: '0.5rem' }}
                />
                <span>{slot.datetime}</span>
              </label>
            ))}
          </div>
          <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
            Selected: {selectedSlots.length} slot(s)
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
          <button
            type="button"
            onClick={onClose}
            className="btn btn-secondary"
            disabled={saving}
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="btn btn-primary"
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  )
}

