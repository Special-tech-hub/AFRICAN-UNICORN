import { useEffect, useState } from 'react'
import { useAuthStore } from '../../store/authStore'
import { getMyApplication, getApplicationStatus } from '../../api/onboarding'

const STATUS_COLORS: Record<string, string> = {
  DRAFT: 'bg-gray-100 text-gray-700',
  SUBMITTED: 'bg-blue-100 text-blue-700',
  UNDER_REVIEW: 'bg-yellow-100 text-yellow-700',
  APPROVED: 'bg-green-100 text-green-700',
  REJECTED: 'bg-red-100 text-red-700',
}

export default function ApplicationStatusPage() {
  const { logout } = useAuthStore()
  const [application, setApplication] = useState<Record<string, unknown> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchStatus = async () => {
    try {
      const appResp = await getMyApplication()
      const app = appResp.data
      const statusResp = await getApplicationStatus(app.id as string)
      setApplication(statusResp.data)
    } catch {
      setError('Could not load your application status.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
    // Auto-refresh every 30s while under review
    const interval = setInterval(() => {
      if (application && ['SUBMITTED', 'UNDER_REVIEW'].includes(application.status as string)) {
        fetchStatus()
      }
    }, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <p className="text-gray-500">Loading your application...</p>
    </div>
  )

  if (error) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg">{error}</div>
    </div>
  )

  const appStatus = application?.status as string
  const history = (application?.status_history as Array<Record<string, unknown>>) || []
  const applicationReference = typeof application?.application_reference === 'string' ? application.application_reference : ''
  const reviewNote = typeof application?.review_note === 'string' ? application.review_note : ''

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center">
        <h1 className="text-lg font-bold text-gray-900">TakeOFF Driver</h1>
        <button onClick={logout} className="text-sm text-gray-500 hover:text-gray-700">Sign out</button>
      </header>
      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-white rounded-2xl shadow-sm p-8">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-xl font-bold text-gray-900">Application Status</h2>
              {applicationReference && (
                <p className="text-gray-500 text-sm mt-1">Ref: {applicationReference}</p>
              )}
            </div>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${STATUS_COLORS[appStatus] || 'bg-gray-100 text-gray-700'}`}>
              {appStatus?.replace('_', ' ')}
            </span>
          </div>

          {appStatus === 'APPROVED' && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <p className="font-semibold text-green-800">🎉 Congratulations! Your application has been approved.</p>
              {reviewNote && (
                <p className="text-green-700 text-sm mt-1">Note: {reviewNote}</p>
              )}
            </div>
          )}

          {appStatus === 'REJECTED' && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="font-semibold text-red-800">Application Rejected</p>
              <p className="text-red-700 text-sm mt-1">Reason: {application?.review_note as string || 'No reason provided.'}</p>
            </div>
          )}

          {history.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Timeline</h3>
              <div className="space-y-3">
                {history.map((h, i) => (
                  <div key={i} className="flex items-center gap-3 text-sm">
                    <span className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0" />
                    <span className="text-gray-600">{(h.new_status as string).replace('_', ' ')}</span>
                    <span className="text-gray-400 text-xs">{new Date(h.created_at as string).toLocaleDateString()}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
