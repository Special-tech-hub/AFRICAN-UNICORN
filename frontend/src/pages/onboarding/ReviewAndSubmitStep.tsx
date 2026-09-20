import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getProfile, getIdentity, getVehicle, getMyApplication, submitApplication } from '../../api/onboarding'
import { listDocuments } from '../../api/documents'

export default function ReviewAndSubmitStep() {
  const navigate = useNavigate()
  const [profile, setProfile] = useState<Record<string, unknown> | null>(null)
  const [identity, setIdentity] = useState<Record<string, unknown> | null>(null)
  const [vehicle, setVehicle] = useState<Record<string, unknown> | null>(null)
  const [documents, setDocuments] = useState<Record<string, unknown>[]>([])
  const [application, setApplication] = useState<Record<string, unknown> | null>(null)
  const [confirmed, setConfirmed] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([
      getProfile().then(r => setProfile(r.data)).catch(() => {}),
      getIdentity().then(r => setIdentity(r.data)).catch(() => {}),
      getVehicle().then(r => setVehicle(r.data)).catch(() => {}),
      listDocuments().then(r => setDocuments(r.data)).catch(() => {}),
      getMyApplication().then(r => setApplication(r.data)).catch(() => {}),
    ])
  }, [])

  const handleSubmit = async () => {
    if (!application) return
    setSubmitting(true)
    setError('')
    try {
      const resp = await submitApplication(application.id as string)
      const ref = resp.data.application_reference
      navigate('/application/success', { state: { reference: ref } })
    } catch (err: unknown) {
      const e = err as { response?: { data?: { message?: string; missing?: string[] } } }
      const missing = e.response?.data?.missing
      if (missing && missing.length > 0) {
        setError('Missing required items:\n• ' + missing.join('\n• '))
      } else {
        setError(e.response?.data?.message || 'Submission failed. Please try again.')
      }
      setShowModal(false)
    } finally {
      setSubmitting(false)
    }
  }

  const SectionRow = ({ label, value }: { label: string; value: unknown }) => (
    <div className="flex justify-between py-1.5 border-b border-gray-50 last:border-0">
      <span className="text-sm text-gray-500">{label}</span>
      <span className="text-sm font-medium text-gray-900">{String(value || '—')}</span>
    </div>
  )

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl shadow-sm p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-gray-900">Personal Information</h3>
          <button onClick={() => navigate('/onboarding/personal')} className="text-blue-600 hover:underline text-sm">Edit</button>
        </div>
        {profile && <>
          <SectionRow label="Full Name" value={`${profile.first_name} ${profile.last_name}`} />
          <SectionRow label="Date of Birth" value={profile.date_of_birth as string} />
          <SectionRow label="Gender" value={profile.gender as string} />
          <SectionRow label="Nationality" value={profile.nationality as string} />
        </>}
      </div>

      <div className="bg-white rounded-2xl shadow-sm p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-gray-900">Contact Details</h3>
          <button onClick={() => navigate('/onboarding/contact')} className="text-blue-600 hover:underline text-sm">Edit</button>
        </div>
        {profile && <>
          <SectionRow label="Email" value={profile.email as string} />
          <SectionRow label="Address" value={`${profile.street_address}, ${profile.city}`} />
          <SectionRow label="Emergency Contact" value={`${profile.emergency_contact_name} (${profile.emergency_contact_phone})`} />
        </>}
      </div>

      <div className="bg-white rounded-2xl shadow-sm p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-gray-900">Identity</h3>
          <button onClick={() => navigate('/onboarding/identity')} className="text-blue-600 hover:underline text-sm">Edit</button>
        </div>
        {identity && <>
          <SectionRow label="ID Type" value={identity.id_type as string} />
          <SectionRow label="ID Number" value={identity.id_number as string} />
          <SectionRow label="Licence Number" value={identity.drivers_license_number as string} />
          <SectionRow label="Licence Expiry" value={identity.license_expiry_date as string} />
        </>}
      </div>

      <div className="bg-white rounded-2xl shadow-sm p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-gray-900">Vehicle</h3>
          <button onClick={() => navigate('/onboarding/vehicle')} className="text-blue-600 hover:underline text-sm">Edit</button>
        </div>
        {vehicle && <>
          <SectionRow label="Type" value={vehicle.vehicle_type as string} />
          <SectionRow label="Make / Model" value={`${vehicle.make} ${vehicle.model} (${vehicle.year})`} />
          <SectionRow label="Registration" value={vehicle.registration_number as string} />
          <SectionRow label="Colour" value={vehicle.colour as string} />
        </>}
      </div>

      <div className="bg-white rounded-2xl shadow-sm p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-gray-900">Documents</h3>
          <button onClick={() => navigate('/onboarding/documents')} className="text-blue-600 hover:underline text-sm">Edit</button>
        </div>
        {documents.length === 0 ? (
          <p className="text-sm text-red-500">No documents uploaded.</p>
        ) : (
          <div className="space-y-2">
            {documents.map((doc) => (
              <div key={doc.id as string} className="flex items-center gap-2 text-sm">
                <span className="text-green-600">✓</span>
                <span className="text-gray-600">{(doc.document_type as string).replace('_', ' ')}</span>
                <span className="text-gray-400 text-xs">— {doc.original_filename as string}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm whitespace-pre-line">
          {error}
        </div>
      )}

      <div className="bg-white rounded-2xl shadow-sm p-6">
        <label className="flex items-start gap-3 cursor-pointer">
          <input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)}
            className="mt-0.5 w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
          <span className="text-sm text-gray-700">
            I confirm that all the information I have provided is accurate and complete.
          </span>
        </label>
      </div>

      <div className="flex justify-between">
        <button onClick={() => navigate('/onboarding/documents')}
          className="border border-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-50 transition-colors">← Back</button>
        <button onClick={() => setShowModal(true)} disabled={!confirmed}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed text-white font-medium px-8 py-2 rounded-lg transition-colors">
          Submit Application
        </button>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 px-4">
          <div className="bg-white rounded-xl p-6 max-w-md w-full">
            <h3 className="font-bold text-gray-900 mb-2">Submit Application?</h3>
            <p className="text-gray-500 text-sm mb-5">You will not be able to edit your application after submission.</p>
            <div className="flex gap-3">
              <button onClick={() => setShowModal(false)}
                className="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-50">Cancel</button>
              <button onClick={handleSubmit} disabled={submitting}
                className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium py-2 rounded-lg">
                {submitting ? 'Submitting...' : 'Submit Application'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
