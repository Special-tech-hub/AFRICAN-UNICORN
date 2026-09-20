import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, accessToken } = useAuthStore()
  const location = useLocation()
  if (!accessToken || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  return <>{children}</>
}

export function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user, accessToken } = useAuthStore()
  const location = useLocation()
  if (!accessToken || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  if (user.role !== 'ADMIN') {
    return <Navigate to="/application/status" replace />
  }
  return <>{children}</>
}
