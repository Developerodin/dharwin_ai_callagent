'use client'

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
  applicationDate: string
}

interface CandidateCardProps {
  candidate: Candidate
  onCall: () => void
  isCalling: boolean
  onReset?: () => void
  onManageSlots?: () => void
  onDelete?: () => void
}

export default function CandidateCard({ candidate, onCall, isCalling, onReset, onManageSlots, onDelete }: CandidateCardProps) {
  const getStatusLabel = (status: string) => {
    switch (status.toLowerCase()) {
      case 'confirmed':
        return '✓ Confirmed'
      case 'declined':
        return '✗ Declined'
      case 'rescheduled':
        return '🔄 Rescheduled'
      case 'calling':
        return '📞 Calling...'
      case 'no_answer':
      case 'no-answer':
      case 'no answer':
        return '📵 No Answer'
      default:
        return '⏳ Pending'
    }
  }
  
  const getStatusClass = (status: string) => {
    switch (status.toLowerCase()) {
      case 'confirmed':
        return 'status-confirmed'
      case 'declined':
        return 'status-declined'
      case 'rescheduled':
        return 'status-rescheduled'
      case 'calling':
        return 'status-calling'
      case 'no_answer':
      case 'no-answer':
      case 'no answer':
        return 'status-no-answer'
      default:
        return 'status-pending'
    }
  }

  return (
    <div className="card" style={{ 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center',
      flexWrap: 'wrap',
      gap: '1rem'
    }}>
      <div style={{ flex: 1, minWidth: '250px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>
            {candidate.name}
          </h3>
          <span className={`status-badge ${getStatusClass(candidate.status)}`}>
            {getStatusLabel(candidate.status)}
          </span>
        </div>
        <div style={{ color: '#666', fontSize: '0.9rem', marginBottom: '0.25rem' }}>
          📧 {candidate.email}
        </div>
        <div style={{ color: '#666', fontSize: '0.9rem', marginBottom: '0.25rem' }}>
          📱 {candidate.phone}
        </div>
        <div style={{ color: '#666', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
          💼 {candidate.position}
        </div>
        <div style={{ 
          background: '#f8f9fa', 
          padding: '0.75rem', 
          borderRadius: '8px',
          marginTop: '0.5rem'
        }}>
          {candidate.status === 'rescheduled' && candidate.originalInterview ? (
            <>
              <div style={{ fontSize: '0.875rem', color: '#666', marginBottom: '0.5rem' }}>
                <strong>Original Interview:</strong>
              </div>
              <div style={{ 
                fontSize: '0.85rem', 
                color: '#856404', 
                marginBottom: '0.75rem',
                padding: '0.5rem',
                background: '#fff3cd',
                borderRadius: '4px',
                borderLeft: '3px solid #ffc107'
              }}>
                📅 {candidate.originalInterview.datetime}
              </div>
              <div style={{ fontSize: '0.875rem', color: '#666', marginBottom: '0.5rem' }}>
                <strong>Rescheduled Interview:</strong>
              </div>
              <div style={{ 
                fontWeight: 600, 
                color: '#155724',
                padding: '0.5rem',
                background: '#d4edda',
                borderRadius: '4px',
                borderLeft: '3px solid #28a745'
              }}>
                📅 {candidate.scheduledInterview.datetime}
              </div>
            </>
          ) : (
            <>
              <div style={{ fontSize: '0.875rem', color: '#666', marginBottom: '0.25rem' }}>
                Scheduled Interview:
              </div>
              <div style={{ fontWeight: 600, color: '#333' }}>
                📅 {candidate.scheduledInterview.datetime}
              </div>
            </>
          )}
        </div>
      </div>
      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
        <button
          className="btn btn-primary"
          onClick={onCall}
          disabled={isCalling || candidate.status === 'calling'}
          style={{ minWidth: '120px' }}
        >
          {isCalling ? (
            <>
              <span className="loading" style={{ marginRight: '0.5rem' }}></span>
              Calling...
            </>
          ) : (
            '📞 Call Now'
          )}
        </button>
        <button
          className="btn btn-secondary"
          onClick={onManageSlots}
          style={{ minWidth: '140px' }}
        >
          📅 Manage Slots
        </button>
        <button
          className="btn btn-secondary"
          onClick={onReset}
          style={{ 
            minWidth: '100px',
            backgroundColor: '#f59e0b',
            color: 'white',
            border: 'none'
          }}
          onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#d97706'}
          onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#f59e0b'}
        >
          🔄 Reset
        </button>
        <button
          className="btn btn-secondary"
          onClick={onDelete}
          style={{ 
            minWidth: '100px',
            backgroundColor: '#ef4444',
            color: 'white',
            border: 'none'
          }}
          onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#dc2626'}
          onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#ef4444'}
        >
          🗑️ Remove
        </button>
      </div>
    </div>
  )
}

