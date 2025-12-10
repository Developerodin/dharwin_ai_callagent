'use client'

import { useState, useEffect } from 'react'
import CandidateList from '@/components/CandidateList'
import CallStatus from '@/components/CallStatus'
import AddCandidateModal from '@/components/AddCandidateModal'
import { getFlaskBackendUrl } from '@/lib/config'

export default function Home() {
  const [candidates, setCandidates] = useState<any[]>([])
  const [availableSlots, setAvailableSlots] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [callStatus, setCallStatus] = useState<any>(null)
  const [showAddModal, setShowAddModal] = useState(false)

  useEffect(() => {
    fetchCandidates()
  }, [])

  const fetchCandidates = async () => {
    try {
      // Add timestamp to force fresh fetch (cache busting)
      const timestamp = new Date().getTime()
      const response = await fetch(`/api/candidates?t=${timestamp}`, {
        cache: 'no-store',
        headers: {
          'Cache-Control': 'no-cache',
        }
      })
      const data = await response.json()
      setCandidates(data.candidates || [])
      setAvailableSlots(data.availableSlots || [])
      console.log(`✅ Fetched ${data.candidates?.length || 0} candidates at ${new Date().toLocaleTimeString()}`)
    } catch (error) {
      console.error('Error fetching candidates:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCallInitiated = (status: any) => {
    setCallStatus(status)
  }

  const handleCallComplete = () => {
    setCallStatus(null)
    // Refresh the list immediately and keep refreshing
    fetchCandidates()
    // Also refresh after delay to catch backend updates
    setTimeout(() => {
      fetchCandidates()
    }, 2000)
    setTimeout(() => {
      fetchCandidates()
    }, 5000)
  }

  const resetStatuses = async () => {
    try {
      const backendUrl = getFlaskBackendUrl()
      const response = await fetch(`${backendUrl}/api/reset-statuses`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const result = await response.json();
      if (result.success) {
        alert(`All statuses reset to pending! (${result.reset_count || 0} candidates updated)`);
        
        // Wait a bit to ensure Flask has written the file, then refresh
        setTimeout(() => {
          // Add timestamp to force fresh fetch (cache busting)
          fetchCandidates();
        }, 500);
        
        // Also refresh after a longer delay as backup
        setTimeout(() => {
          fetchCandidates();
        }, 1500);
      } else {
        alert('Error: ' + result.error);
      }
    } catch (error) {
      alert('Failed to reset statuses: ' + error);
    }
  }
  
  // Auto-refresh candidates periodically to catch status updates
  useEffect(() => {
    const interval = setInterval(() => {
      fetchCandidates()
    }, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="container">
      <header style={{ 
        textAlign: 'center', 
        color: 'white', 
        marginBottom: '2rem',
        padding: '2rem 0'
      }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>
          📞 Dharwin Interview Scheduler
        </h1>
        <p style={{ fontSize: '1.2rem', opacity: 0.9 }}>
          Powered by Ava - Your AI Interview Assistant
        </p>
      </header>

      {callStatus && (
        <CallStatus 
          status={callStatus} 
          onClose={handleCallComplete}
          onRefresh={fetchCandidates}
        />
      )}

      <div className="card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
          <h2 style={{ fontSize: '1.5rem', margin: 0 }}>
            Candidate List
          </h2>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={() => setShowAddModal(true)}
              className="btn btn-primary"
              style={{ minWidth: '140px' }}
            >
              ➕ Add Candidate
            </button>
            <button
              onClick={resetStatuses}
              style={{
                backgroundColor: '#ef4444',
                color: 'white',
                border: 'none',
                padding: '0.5rem 1rem',
                borderRadius: '0.375rem',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: 'bold'
              }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#dc2626'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#ef4444'}
            >
              Reset All Statuses to Pending
            </button>
          </div>
        </div>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <div className="loading" style={{ margin: '0 auto' }}></div>
            <p style={{ marginTop: '1rem' }}>Loading candidates...</p>
          </div>
        ) : (
          <CandidateList 
            candidates={candidates}
            availableSlots={availableSlots}
            onCallInitiated={handleCallInitiated}
            onStatusUpdate={fetchCandidates}
          />
        )}
      </div>

      <AddCandidateModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSuccess={fetchCandidates}
        availableSlots={availableSlots}
      />
    </div>
  )
}

