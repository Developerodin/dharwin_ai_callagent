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

interface AddCandidateModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  availableSlots: AvailableSlot[]
}

export default function AddCandidateModal({ isOpen, onClose, onSuccess, availableSlots }: AddCandidateModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    position: '',
    interviewDate: '',
    interviewTime: '',
    interviewDay: '',
    applicationDate: new Date().toISOString().split('T')[0],
    reschedulingSlots: [] as number[]
  })

  const [selectedSlotId, setSelectedSlotId] = useState<number | null>(null)

  useEffect(() => {
    if (selectedSlotId) {
      const slot = availableSlots.find(s => s.id === selectedSlotId)
      if (slot) {
        setFormData(prev => ({
          ...prev,
          interviewDate: slot.date,
          interviewTime: slot.time,
          interviewDay: slot.day
        }))
      }
    }
  }, [selectedSlotId, availableSlots])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      const backendUrl = getFlaskBackendUrl()
      const response = await fetch(`${backendUrl}/api/candidate/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          phone: formData.phone,
          email: formData.email,
          position: formData.position,
          scheduledInterview: {
            date: formData.interviewDate,
            time: formData.interviewTime,
            day: formData.interviewDay,
            datetime: `${formData.interviewDate} at ${formData.interviewTime}`
          },
          applicationDate: formData.applicationDate,
          reschedulingSlots: formData.reschedulingSlots
        }),
      })

      const data = await response.json()
      
      if (data.success) {
        alert('Candidate added successfully!')
        setFormData({
          name: '',
          phone: '',
          email: '',
          position: '',
          interviewDate: '',
          interviewTime: '',
          interviewDay: '',
          applicationDate: new Date().toISOString().split('T')[0],
          reschedulingSlots: []
        })
        setSelectedSlotId(null)
        onSuccess()
        onClose()
      } else {
        alert(`Error: ${data.error || 'Failed to add candidate'}`)
      }
    } catch (error) {
      console.error('Error adding candidate:', error)
      alert('Failed to add candidate. Please try again.')
    }
  }

  const toggleReschedulingSlot = (slotId: number) => {
    setFormData(prev => {
      const current = prev.reschedulingSlots
      const newSlots = current.includes(slotId)
        ? current.filter(id => id !== slotId)
        : [...current, slotId]
      return { ...prev, reschedulingSlots: newSlots }
    })
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
        maxWidth: '600px',
        width: '90%',
        maxHeight: '90vh',
        overflowY: 'auto'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Add New Candidate</h2>
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

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
              Name *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #ddd',
                borderRadius: '4px'
              }}
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
              Phone *
            </label>
            <input
              type="tel"
              required
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              placeholder="+919876543210"
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #ddd',
                borderRadius: '4px'
              }}
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
              Email *
            </label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #ddd',
                borderRadius: '4px'
              }}
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
              Position *
            </label>
            <input
              type="text"
              required
              value={formData.position}
              onChange={(e) => setFormData({ ...formData, position: e.target.value })}
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #ddd',
                borderRadius: '4px'
              }}
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
              Scheduled Interview Slot *
            </label>
            <select
              required
              value={selectedSlotId || ''}
              onChange={(e) => setSelectedSlotId(Number(e.target.value) || null)}
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #ddd',
                borderRadius: '4px'
              }}
            >
              <option value="">Select a slot</option>
              {availableSlots.map(slot => (
                <option key={slot.id} value={slot.id}>
                  {slot.datetime}
                </option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
              Rescheduling Slots (Select multiple)
            </label>
            <div style={{
              border: '1px solid #ddd',
              borderRadius: '4px',
              padding: '0.5rem',
              maxHeight: '200px',
              overflowY: 'auto'
            }}>
              {availableSlots.map(slot => (
                <label key={slot.id} style={{ display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <input
                    type="checkbox"
                    checked={formData.reschedulingSlots.includes(slot.id)}
                    onChange={() => toggleReschedulingSlot(slot.id)}
                    style={{ marginRight: '0.5rem' }}
                  />
                  <span>{slot.datetime}</span>
                </label>
              ))}
            </div>
            {formData.reschedulingSlots.length > 0 && (
              <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#666' }}>
                Selected: {formData.reschedulingSlots.length} slot(s)
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
            >
              Add Candidate
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

