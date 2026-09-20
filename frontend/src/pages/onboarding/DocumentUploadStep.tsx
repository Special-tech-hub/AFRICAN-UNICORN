import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listDocuments, uploadDocument, deleteDocument } from '../../api/documents'

const REQUIRED_DOCS = [
  { type: 'NATIONAL_ID', label: 'National ID / Passport', required: true },
  { type: 'DRIVERS_LICENSE', label: "Driver's Licence", required: true },
  { type: 'VEHICLE_REGISTRATION', label: 'Vehicle Registration', required: true },
  { type: 'INSURANCE', label: 'Insurance Certificate', required: true },
  { type: 'INSPECTION', label: 'Vehicle Inspection Certificate', required: false },
]

interface DocEntry {
  id: string
  document_type: string
  original_filename: string
}

export default function DocumentUploadStep() {
  const navigate = useNavigate()
  const [uploaded, setUploaded] = useState<Record<string, DocEntry>>({})
  const [uploading, setUploading] = useState<Record<string, boolean>>({})
  const [errors, setErrors] = useState<Record<string, string>>({})

  const loadDocs = async () => {
    const resp = await listDocuments()
    const map: Record<string, DocEntry> = {}
    for (const doc of resp.data) {
      map[doc.document_type] = doc
    }
    setUploaded(map)
  }

  useEffect(() => { loadDocs() }, [])

  const handleFileChange = async (docType: string, file: File | null) => {
    if (!file) return
    if (file.size > 10 * 1024 * 1024) {
      setErrors(e => ({ ...e, [docType]: 'File size must be under 10 MB.' }))
      return
    }
    setErrors(e => ({ ...e, [docType]: '' }))
    setUploading(u => ({ ...u, [docType]: true }))
    try {
      await uploadDocument(docType, file)
      await loadDocs()
    } catch (err: unknown) {
      const e = err as { response?: { data?: { message?: string } } }
      setErrors(prev => ({ ...prev, [docType]: e.response?.data?.message || 'Upload failed.' }))
    } finally {
      setUploading(u => ({ ...u, [docType]: false }))
    }
  }

  const handleDelete = async (docType: string, docId: string) => {
    try {
      await deleteDocument(docId)
      setUploaded(u => { const copy = { ...u }; delete copy[docType]; return copy })
    } catch {
      setErrors(e => ({ ...e, [docType]: 'Could not delete document.' }))
    }
  }

  const requiredComplete = REQUIRED_DOCS.filter(d => d.required).every(d => uploaded[d.type])

  return (
    <div className="bg-white rounded-2xl shadow-sm p-8">
      <h2 className="text-xl font-bold text-gray-900 mb-2">Required Documents</h2>
      <p className="text-sm text-gray-500 mb-6">Upload test/fictional files only. Accepted: PDF, JPG, PNG (max 10 MB).</p>

      <div className="space-y-4">
        {REQUIRED_DOCS.map(({ type, label, required }) => {
          const doc = uploaded[type]
          const isUploading = uploading[type]
          const error = errors[type]
          return (
            <div key={type} className={`border rounded-xl p-4 ${doc ? 'border-green-200 bg-green-50' : 'border-gray-200'}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-800">{label}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${required ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-500'}`}>
                  {required ? 'Required' : 'Optional'}
                </span>
              </div>

              {doc ? (
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-green-600 text-lg">✓</span>
                    <span className="text-sm text-gray-600 truncate max-w-xs">{doc.original_filename}</span>
                  </div>
                  <button onClick={() => handleDelete(type, doc.id)}
                    className="text-xs text-red-500 hover:text-red-700">Remove</button>
                </div>
              ) : (
                <label className="cursor-pointer">
                  <div className={`border-2 border-dashed rounded-lg p-3 text-center transition-colors ${isUploading ? 'border-blue-300 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}`}>
                    {isUploading ? (
                      <span className="text-sm text-blue-500">Uploading...</span>
                    ) : (
                      <span className="text-sm text-gray-400">Click to select file</span>
                    )}
                  </div>
                  <input type="file" accept=".pdf,.jpg,.jpeg,.png" className="hidden"
                    disabled={isUploading}
                    onChange={(e) => handleFileChange(type, e.target.files?.[0] || null)} />
                </label>
              )}
              {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
            </div>
          )
        })}
      </div>

      <div className="flex justify-between mt-8">
        <button onClick={() => navigate('/onboarding/vehicle')}
          className="border border-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-50 transition-colors">← Back</button>
        <button onClick={() => navigate('/onboarding/review')} disabled={!requiredComplete}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed text-white font-medium px-6 py-2 rounded-lg transition-colors">
          {requiredComplete ? 'Review Application →' : 'Upload required documents first'}
        </button>
      </div>
    </div>
  )
}
