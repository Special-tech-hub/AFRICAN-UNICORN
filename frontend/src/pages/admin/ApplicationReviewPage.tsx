import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getApplication, approveApplication, rejectApplication } from '../../api/admin'
import { useAuthStore } from '../../store/authStore'

const STATUS_COLORS: Record<string, string> = {
  DRAFT: 'bg-gray-100 text-gray-700',
  SUBMITTED: 'bg-blue-100 text-blue-700',
  UNDER_REVIEW: 'bg-yellow-100 text-yellow-700',
  APPROVED: 'bg-green-100 text-green-700',
  REJECTED: 'bg-red-100 text-red-700',
}

export default function ApplicationReviewPage() {
  const { id } = useParams<{ id: string }>()
  const { logout } = useAuthStore()
  const [app, setApp] = useState<Record<string, unknown> | null>(null)
  const [loading, setLoading] = useState(true)
  const [showApproveModal, setShowApproveModal] = useState(false)
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [approveNote, setApproveNote] = useState('')
  const [rejectReason, setRejectReason] = useState('')
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (id) getApplication(id).then((r) => setApp(r.data)).catch(() => {}).finally(() => setLoading(false))
  }, [id])

  const handleApprove = async () => {
    setActionLoading(true); setError('')
    try {
      const r = await approveApplication(id!, approveNote)
      setApp(r.data); setShowApproveModal(false)
    } catch { setError('Failed to approve application.') }
    finally { setActionLoading(false) }
  }

  const handleReject = async () => {
    if (!rejectReason.trim()) { setError('A rejection reason is required.'); return }
    setActionLoading(true); setError('')
    try {
      const r = await rejectApplication(id!, rejectReason)
      setApp(r.data); setShowRejectModal(false)
    } catch { setError('Failed to reject application.') }
    finally { setActionLoading(false) }
  }

  if (loading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center"><p className="text-gray-500">Loading...</p></div>

  const profile = app?.profile as Record<string, string> | null
  const identity = app?.identity as Record<string, unknown> | null
  const vehicle = app?.vehicle as Record<string, unknown> | null
  const documents = (app?.documents as Record<string, unknown>[]) || []
  const history = (app?.status_history as Record<string, unknown>[]) || []
  const appStatus = app?.status as string

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <Link to="/admin/applications" className="text-sm text-gray-500 hover:text-gray-700">← Applications</Link>
          <span className="text-gray-300">|</span>
          <span className="text-sm font-medium">{app?.application_reference as string || 'Application'}</span>
        </div>
        <button onClick={logout} className="text-sm text-gray-500 hover:text-gray-700">Sign out</button>
      </header>
      <main className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        {/* Status banner */}
        <div className="bg-white rounded-xl border p-5 flex justify-between items-center">
          <div>
            <p className="text-sm text-gray-500">Application Reference</p>
            <p className="font-bold text-gray-900">{(app?.application_reference as string) || '—'}</p>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${STATUS_COLORS[appStatus] || ''}`}>
            {appStatus?.replace('_', ' ')}
          </span>
        </div>

        {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}

        {/* Profile */}
        {profile && (
          <section className="bg-white rounded-xl border p-5">
            <h3 className="font-semibold text-gray-900 mb-3">Driver Information</h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div><span className="text-gray-500">Name:</span> <span className="font-medium">{profile.first_name} {profile.last_name}</span></div>
              <div><span className="text-gray-500">Phone:</span> <span>{app?.driver_phone as string}</span></div>
              <div><span className="text-gray-500">Email:</span> <span>{profile.email}</span></div>
              <div><span className="text-gray-500">City:</span> <span>{profile.city}</span></div>
            </div>
          </section>
        )}

        {/* Identity */}
        {identity && (
          <section className="bg-white rounded-xl border p-5">
            <h3 className="font-semibold text-gray-900 mb-3">Identity Verification</h3>
            {(identity.is_license_expired as boolean) && (
              <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-3 py-2 rounded text-sm mb-3">
                ⚠ Driver's licence is expired
              </div>
            )}
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div><span className="text-gray-500">ID Type:</span> <span>{identity.id_type as string}</span></div>
              <div><span className="text-gray-500">ID Number:</span> <span>{identity.id_number as string}</span></div>
              <div><span className="text-gray-500">Licence No:</span> <span>{identity.drivers_license_number as string}</span></div>
              <div><span className="text-gray-500">Expiry:</span> <span>{identity.license_expiry_date as string}</span></div>
            </div>
          </section>
        )}

        {/* Vehicle */}
        {vehicle && (
          <section className="bg-white rounded-xl border p-5">
            <h3 className="font-semibold text-gray-900 mb-3">Vehicle Details</h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div><span className="text-gray-500">Type:</span> <span>{vehicle.vehicle_type as string}</span></div>
              <div><span className="text-gray-500">Make/Model:</span> <span>{vehicle.make as string} {vehicle.model as string}</span></div>
              <div><span className="text-gray-500">Year:</span> <span>{vehicle.year as number}</span></div>
              <div><span className="text-gray-500">Registration:</span> <span>{vehicle.registration_number as string}</span></div>
            </div>
          </section>
        )}

        {/* Documents */}
        <section className="bg-white rounded-xl border p-5">
          <h3 className="font-semibold text-gray-900 mb-3">Documents</h3>
          {documents.length === 0 ? <p className="text-gray-400 text-sm">No documents uploaded.</p> : (
            <div className="space-y-2">
              {documents.map((doc) => (
                <div key={doc.id as string} className="flex justify-between items-center text-sm border rounded-lg px-3 py-2">
                  <span className="text-gray-700">{(doc.document_type as string).replace('_', ' ')}</span>
                  <a href={doc.download_url as string} target="_blank" rel="noopener noreferrer"
                    className="text-blue-600 hover:underline text-xs">Download</a>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* History */}
        {history.length > 0 && (
          <section className="bg-white rounded-xl border p-5">
            <h3 className="font-semibold text-gray-900 mb-3">Application History</h3>
            <div className="space-y-2">
              {history.map((h, i) => {
                const status = typeof h.new_status === 'string' ? h.new_status.replace('_', ' ') : ''
                const createdAt = typeof h.created_at === 'string' ? new Date(h.created_at).toLocaleDateString() : ''
                const note = typeof h.note === 'string' ? h.note : ''

                return (
                  <div key={i} className="flex items-center gap-3 text-sm">
                    <span className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0" />
                    <span className="text-gray-700">{status}</span>
                    <span className="text-gray-400 text-xs">{createdAt}</span>
                    {note && <span className="text-gray-500 italic text-xs">— {note}</span>}
                  </div>
                )
              })}
            </div>
          </section>
        )}

        {/* Actions */}
        {appStatus === 'UNDER_REVIEW' && (
          <div className="flex gap-3">
            <button onClick={() => setShowApproveModal(true)} className="flex-1 bg-green-600 hover:bg-green-700 text-white font-medium py-2 rounded-lg transition-colors">
              Approve Application
            </button>
            <button onClick={() => setShowRejectModal(true)} className="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium py-2 rounded-lg transition-colors">
              Reject Application
            </button>
          </div>
        )}
      </main>

      {/* Approve Modal */}
      {showApproveModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 px-4">
          <div className="bg-white rounded-xl p-6 max-w-md w-full">
            <h3 className="font-bold text-gray-900 mb-3">Approve Application?</h3>
            <textarea value={approveNote} onChange={(e) => setApproveNote(e.target.value)}
              placeholder="Optional approval note..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-green-500" rows={3} />
            <div className="flex gap-3">
              <button onClick={() => setShowApproveModal(false)} className="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg">Cancel</button>
              <button onClick={handleApprove} disabled={actionLoading} className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-green-300 text-white py-2 rounded-lg">
                {actionLoading ? 'Approving...' : 'Approve'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 px-4">
          <div className="bg-white rounded-xl p-6 max-w-md w-full">
            <h3 className="font-bold text-gray-900 mb-3">Reject Application?</h3>
            <textarea value={rejectReason} onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Rejection reason (required)..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-red-500" rows={3} />
            <div className="flex gap-3">
              <button onClick={() => setShowRejectModal(false)} className="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg">Cancel</button>
              <button onClick={handleReject} disabled={actionLoading || !rejectReason.trim()} className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-red-300 text-white py-2 rounded-lg">
                {actionLoading ? 'Rejecting...' : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
