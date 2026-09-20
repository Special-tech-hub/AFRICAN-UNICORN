import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ProtectedRoute, AdminRoute } from './components/ProtectedRoute'
import RegisterPage from './pages/auth/RegisterPage'
import OTPVerifyPage from './pages/auth/OTPVerifyPage'
import LoginPage from './pages/auth/LoginPage'
import OnboardingLayout from './components/onboarding/OnboardingLayout'
import PersonalDetailsStep from './pages/onboarding/PersonalDetailsStep'
import SubmissionSuccessPage from './pages/application/SubmissionSuccessPage'
import ApplicationStatusPage from './pages/application/ApplicationStatusPage'
import AdminDashboardPage from './pages/admin/AdminDashboardPage'
import ApplicationListPage from './pages/admin/ApplicationListPage'
import ApplicationReviewPage from './pages/admin/ApplicationReviewPage'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify-otp" element={<OTPVerifyPage />} />
        <Route path="/login" element={<LoginPage />} />

        {/* Driver onboarding */}
        <Route path="/onboarding" element={<ProtectedRoute><OnboardingLayout /></ProtectedRoute>}>
          <Route path="personal" element={<PersonalDetailsStep />} />
          <Route index element={<Navigate to="personal" replace />} />
        </Route>

        {/* Driver application status */}
        <Route path="/application/success" element={<ProtectedRoute><SubmissionSuccessPage /></ProtectedRoute>} />
        <Route path="/application/status" element={<ProtectedRoute><ApplicationStatusPage /></ProtectedRoute>} />

        {/* Admin */}
        <Route path="/admin/dashboard" element={<AdminRoute><AdminDashboardPage /></AdminRoute>} />
        <Route path="/admin/applications" element={<AdminRoute><ApplicationListPage /></AdminRoute>} />
        <Route path="/admin/applications/:id" element={<AdminRoute><ApplicationReviewPage /></AdminRoute>} />

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  )
}

export default App
