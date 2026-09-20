import { Outlet, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

const STEPS = [
  { id: 1, label: 'Personal', path: '/onboarding/personal' },
  { id: 2, label: 'Contact', path: '/onboarding/contact' },
  { id: 3, label: 'Identity', path: '/onboarding/identity' },
  { id: 4, label: 'Vehicle', path: '/onboarding/vehicle' },
  { id: 5, label: 'Documents', path: '/onboarding/documents' },
  { id: 6, label: 'Review', path: '/onboarding/review' },
]

function getCurrentStep(pathname: string): number {
  const step = STEPS.find((s) => pathname.startsWith(s.path))
  return step ? step.id : 1
}

export default function OnboardingLayout() {
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const currentStep = getCurrentStep(location.pathname)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center">
        <h1 className="text-lg font-bold text-gray-900">TakeOFF Driver Onboarding</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-500">{user?.phone_number}</span>
          <button onClick={logout} className="text-sm text-gray-500 hover:text-gray-700">Sign out</button>
        </div>
      </header>

      {/* Progress bar */}
      <div className="bg-white border-b px-6 py-4">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center justify-between">
            {STEPS.map((step, idx) => {
              const isDone = step.id < currentStep
              const isCurrent = step.id === currentStep
              return (
                <div key={step.id} className="flex items-center flex-1">
                  <div className="flex flex-col items-center">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium border-2
                      ${isDone ? 'bg-blue-600 border-blue-600 text-white' :
                        isCurrent ? 'border-blue-600 text-blue-600 bg-white' :
                        'border-gray-300 text-gray-400 bg-white'}`}>
                      {isDone ? '✓' : step.id}
                    </div>
                    <span className={`text-xs mt-1 ${isCurrent ? 'text-blue-600 font-medium' : isDone ? 'text-blue-400' : 'text-gray-400'}`}>
                      {step.label}
                    </span>
                  </div>
                  {idx < STEPS.length - 1 && (
                    <div className={`flex-1 h-0.5 mx-2 mb-4 ${step.id < currentStep ? 'bg-blue-600' : 'bg-gray-200'}`} />
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Page content */}
      <main className="max-w-3xl mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
