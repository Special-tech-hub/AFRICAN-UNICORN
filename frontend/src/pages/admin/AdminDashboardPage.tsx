import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getStatistics } from '../../api/admin'
import { useAuthStore } from '../../store/authStore'

export default function AdminDashboardPage() {
  const { logout } = useAuthStore()
  const [stats, setStats] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getStatistics().then((r) => setStats(r.data)).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const statCards = [
    { label: 'Total Applications', value: stats.total || 0, color: 'bg-gray-50', link: '/admin/applications' },
    { label: 'Pending Review', value: (stats.SUBMITTED || 0) + (stats.UNDER_REVIEW || 0), color: 'bg-yellow-50', link: '/admin/applications?status=SUBMITTED' },
    { label: 'Approved', value: stats.APPROVED || 0, color: 'bg-green-50', link: '/admin/applications?status=APPROVED' },
    { label: 'Rejected', value: stats.REJECTED || 0, color: 'bg-red-50', link: '/admin/applications?status=REJECTED' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center">
        <h1 className="text-lg font-bold text-gray-900">TakeOFF Admin</h1>
        <div className="flex gap-4 items-center">
          <Link to="/admin/applications" className="text-sm text-blue-600 hover:underline">Applications</Link>
          <button onClick={logout} className="text-sm text-gray-500 hover:text-gray-700">Sign out</button>
        </div>
      </header>
      <main className="max-w-5xl mx-auto px-4 py-8">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Dashboard</h2>
        {loading ? (
          <p className="text-gray-500">Loading statistics...</p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {statCards.map((card) => (
              <Link key={card.label} to={card.link} className={`${card.color} rounded-xl p-5 border hover:shadow-sm transition-shadow`}>
                <p className="text-3xl font-bold text-gray-900">{card.value}</p>
                <p className="text-sm text-gray-500 mt-1">{card.label}</p>
              </Link>
            ))}
          </div>
        )}
        <div className="bg-white rounded-xl border p-4">
          <h3 className="font-semibold text-gray-900 mb-3">Quick Actions</h3>
          <Link to="/admin/applications?status=SUBMITTED" className="block text-blue-600 hover:underline text-sm py-1">
            → Review submitted applications
          </Link>
          <Link to="/admin/applications?status=UNDER_REVIEW" className="block text-blue-600 hover:underline text-sm py-1">
            → Applications under review
          </Link>
        </div>
      </main>
    </div>
  )
}
