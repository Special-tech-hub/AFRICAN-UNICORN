import { Link, useLocation } from 'react-router-dom'

export default function SubmissionSuccessPage() {
  const location = useLocation()
  const ref = (location.state as { reference?: string })?.reference || ''

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-sm p-10 text-center">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <span className="text-3xl" role="img" aria-label="success">✓</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Application Submitted!</h1>
        <p className="text-gray-500 mb-6">Your application has been submitted and is now awaiting review.</p>
        {ref && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3 mb-6">
            <p className="text-sm text-gray-600">Application Reference</p>
            <p className="text-xl font-bold text-blue-700">{ref}</p>
          </div>
        )}
        <p className="text-sm text-gray-500 mb-6">We will notify you once your application has been reviewed.</p>
        <Link to="/application/status" className="block w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition-colors">
          View Application Status
        </Link>
      </div>
    </div>
  )
}
