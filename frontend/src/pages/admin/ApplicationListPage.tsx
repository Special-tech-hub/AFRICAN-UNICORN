import { useEffect, useState, useCallback } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { listApplications } from '../../api/admin'
import { useAuthStore } from '../../store/authStore'

const STATUS_COLORS: Record<string, string> = {
  DRAFT: 'bg-gray-100 text-gray-700',
  SUBMITTED: 'bg-blue-100 text-blue-700',
  UNDER_REVIEW: 'bg-yellow-100 text-yellow-700',
  APPROVED: 'bg-green-100 text-green-700',
  REJECTED: 'bg-red-100 text-red-700',
}

export default function ApplicationListPage() {
  const { logout } = useAuthStore()
  const [searchParams] = useSearchParams()
  const [applications, setApplications] = useState<Record<string, unknown>[]>([])
  const [count, setCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState(searchParams.get('search') || '')
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || '')
  const [page] = useState(1)

  const fetchApplications = useCallback(async () => {
    setLoading(true)
    try {
      const resp = await listApplications({ status: statusFilter || undefined, search: search || undefined, page })
      setApplications(resp.data.results)
      setCount(resp.data.count)
    } catch {}
    finally { setLoading(false) }
  }, [statusFilter, search, page])

  useEffect(() => {
    const timer = setTimeout(fetchApplications, 300)
    return () => clearTimeout(timer)
  }, [fetchApplications])

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center">
        <h1 className="text-lg font-bold text-gray-900">TakeOFF Admin</h1>
        <div className="flex gap-4 items-center">
          <Link to="/admin/dashboard" className="text-sm text-blue-600 hover:underline">Dashboard</Link>
          <button onClick={logout} className="text-sm text-gray-500 hover:text-gray-700">Sign out</button>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-900">Applications ({count})</h2>
        </div>
        <div className="flex gap-3 mb-6">
          <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by name, phone, or reference..."
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">All Statuses</option>
            {['DRAFT','SUBMITTED','UNDER_REVIEW','APPROVED','REJECTED'].map((s) => (
              <option key={s} value={s}>{s.replace('_',' ')}</option>
            ))}
          </select>
        </div>
        {loading ? <p className="text-gray-500">Loading...</p> : applications.length === 0 ? (
          <div className="bg-white rounded-xl border p-8 text-center">
            <p className="text-gray-500">No applications match your search.</p>
          </div>
        ) : (
          <div className="bg-white rounded-xl border overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  {['Reference','Driver','Phone','Vehicle','Submitted','Status','Action'].map((h) => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {applications.map((app) => (
                  <tr key={app.id as string} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono text-xs">{(app.application_reference as string) || '—'}</td>
                    <td className="px-4 py-3">{app.driver_name as string}</td>
                    <td className="px-4 py-3 text-gray-500">{app.driver_phone as string}</td>
                    <td className="px-4 py-3 text-gray-500">{(app.vehicle_summary as string) || '—'}</td>
                    <td className="px-4 py-3 text-gray-500">{app.submitted_at ? new Date(app.submitted_at as string).toLocaleDateString() : '—'}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[app.status as string] || ''}`}>
                        {(app.status as string).replace('_',' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <Link to={`/admin/applications/${app.id as string}`} className="text-blue-600 hover:underline text-xs">View</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  )
}
