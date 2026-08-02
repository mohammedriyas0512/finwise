import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { FullSpinner } from '../components/Feedback.jsx'

export default function ProtectedRoute({ adminOnly = false, children }) {
  const { user, loading, isAdmin } = useAuth()
  const location = useLocation()

  if (loading) return <FullSpinner label="Authenticating…" />
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />
  if (adminOnly && !isAdmin) return <Navigate to="/dashboard" replace />
  return children
}
