import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { verifyOtp, resendOtp } from '../../api/auth'
import { useAuthStore } from '../../store/authStore'

export default function OTPVerifyPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuthStore()
  const phone = (location.state as { phone_number?: string })?.phone_number || ''

  const [otp, setOtp] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [resendLoading, setResendLoading] = useState(false)
  const [countdown, setCountdown] = useState(60)
  const [canResend, setCanResend] = useState(false)

  useEffect(() => {
    if (countdown > 0) {
      const t = setTimeout(() => setCountdown((c) => c - 1), 1000)
      return () => clearTimeout(t)
    } else {
      setCanResend(true)
    }
  }, [countdown])

  const handleVerify = async () => {
    if (otp.length !== 6) { setError('Please enter the 6-digit OTP.'); return }
    setLoading(true); setError('')
    try {
      const { data } = await verifyOtp({ phone_number: phone, otp })
      login({ access: data.access, refresh: data.refresh }, data.user)
      navigate('/onboarding/personal')
    } catch (err: unknown) {
      const e = err as { response?: { data?: { message?: string } } }
      setError(e.response?.data?.message || 'Invalid OTP. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    setResendLoading(true); setError('')
    try {
      await resendOtp({ phone_number: phone })
      setCountdown(60); setCanResend(false)
    } catch (err: unknown) {
      const e = err as { response?: { data?: { message?: string } } }
      setError(e.response?.data?.message || 'Could not resend OTP.')
    } finally {
      setResendLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-sm p-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Verify Your Phone</h1>
          <p className="text-gray-500 mt-1">We sent a 6-digit code to <span className="font-medium">{phone}</span></p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm mb-4" role="alert">
            {error}
          </div>
        )}

        <div className="space-y-5">
          <div>
            <label htmlFor="otp" className="block text-sm font-medium text-gray-700 mb-1">OTP Code</label>
            <input id="otp" type="text" inputMode="numeric" maxLength={6} value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
              className="w-full border border-gray-300 rounded-lg px-3 py-3 text-center text-2xl tracking-widest focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="000000" aria-label="One-time password" />
          </div>

          <button onClick={handleVerify} disabled={loading || otp.length !== 6}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium py-2 rounded-lg transition-colors">
            {loading ? 'Verifying...' : 'Verify OTP'}
          </button>

          <div className="text-center text-sm">
            {canResend ? (
              <button onClick={handleResend} disabled={resendLoading}
                className="text-blue-600 hover:underline disabled:text-gray-400">
                {resendLoading ? 'Resending...' : 'Resend OTP'}
              </button>
            ) : (
              <span className="text-gray-400">Resend in {countdown}s</span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
