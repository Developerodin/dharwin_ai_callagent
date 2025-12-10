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
      const backendUrl = getFlaskBackendUrl()
      
      // Read directly from Flask backend to ensure we get the latest data
      // This avoids any caching or path mismatch issues
      const timestamp = new Date().getTime()
      const response = await fetch(`${backendUrl}/api/candidates?t=${timestamp}`, {
        cache: 'no-store',
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
        }
      })
      
      if (!response.ok) {
        // Fallback to Next.js API route if Flask is unavailable
        console.warn('Flask backend unavailable, using Next.js API route')
        const fallbackResponse = await fetch(`/api/candidates?t=${timestamp}`, {
          cache: 'no-store',
        })
        const fallbackData = await fallbackResponse.json()
        setCandidates(fallbackData.candidates || [])
        setAvailableSlots(fallbackData.availableSlots || [])
        return
      }
      
      const data = await response.json()
      
      // Log status distribution for debugging
      const statusCounts = (data.candidates || []).reduce((acc: any, c: any) => {
        acc[c.status] = (acc[c.status] || 0) + 1;
        return acc;
      }, {});
      
      console.log(`✅ Fetched ${data.candidates?.length || 0} candidates from Flask at ${new Date().toLocaleTimeString()}`)
      console.log(`   Status breakdown:`, statusCounts)
      
      setCandidates(data.candidates || [])
      setAvailableSlots(data.availableSlots || [])
    } catch (error) {
      console.error('Error fetching candidates:', error)
      // Fallback to Next.js API route on error
      try {
        const fallbackResponse = await fetch('/api/candidates')
        const fallbackData = await fallbackResponse.json()
        setCandidates(fallbackData.candidates || [])
        setAvailableSlots(fallbackData.availableSlots || [])
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError)
      }
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
      console.log(`[Reset] Calling reset endpoint: ${backendUrl}/api/reset-statuses`)
      
      const response = await fetch(`${backendUrl}/api/reset-statuses`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      });
      
      const result = await response.json();
      console.log('[Reset] Response:', result)
      
      if (result.success) {
        alert(`All statuses reset to pending! (${result.reset_count || 0} candidates updated)`);
        
        // Force multiple refreshes with increasing delays to ensure UI updates
        const refreshMultipleTimes = () => {
          fetchCandidates(); // Immediate
          setTimeout(() => fetchCandidates(), 300);  // 300ms
          setTimeout(() => fetchCandidates(), 800);  // 800ms
          setTimeout(() => fetchCandidates(), 1500); // 1.5s
          setTimeout(() => fetchCandidates(), 2500); // 2.5s
        };
        
        refreshMultipleTimes();
        
        // Also try reloading the page as last resort if still not updated
        setTimeout(() => {
          console.log('[Reset] Final refresh check...');
          fetchCandidates();
        }, 3000);
      } else {
        alert('Error: ' + result.error);
      }
    } catch (error) {
      console.error('[Reset] Error:', error);
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

