import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { getIdentity, updateIdentity } from '../../api/onboarding'

const schema = z.object({
  id_type: z.enum(['NATIONAL_ID', 'PASSPORT'], { errorMap: () => ({ message: 'Select an ID type' }) }),
  id_number: z.string().min(1, 'ID number is required'),
  drivers_license_number: z.string().min(1, "Driver's licence number is required"),
  license_expiry_date: z.string().min(1, 'Licence expiry date is required'),
})
type FormData = z.infer<typeof schema>

export default function IdentityVerificationStep() {
  const navigate = useNavigate()
  const { register, handleSubmit, watch, reset, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const expiryDate = watch('license_expiry_date')
  const isExpired = expiryDate && new Date(expiryDate) < new Date()

  useEffect(() => {
    getIdentity().then((r) => { if (r.data.id_type) reset(r.data) }).catch(() => {})
  }, [reset])

  const onSubmit = async (data: FormData) => {
    await updateIdentity(data)
    navigate('/onboarding/vehicle')
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm p-8">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Identity Verification</h2>
      <p className="text-sm text-gray-500 mb-6">Use fictional test data only — do not upload real identity documents.</p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">ID Type <span className="text-red-500">*</span></label>
          <select {...register('id_type')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">Select...</option>
            <option value="NATIONAL_ID">National ID</option>
            <option value="PASSPORT">Passport</option>
          </select>
          {errors.id_type && <p className="text-red-500 text-xs mt-1">{errors.id_type.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">ID Number <span className="text-red-500">*</span></label>
          <input {...register('id_number')} placeholder="e.g. TEST-NID-001" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          {errors.id_number && <p className="text-red-500 text-xs mt-1">{errors.id_number.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Driver's Licence Number <span className="text-red-500">*</span></label>
          <input {...register('drivers_license_number')} placeholder="e.g. TEST-DL-001" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          {errors.drivers_license_number && <p className="text-red-500 text-xs mt-1">{errors.drivers_license_number.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Licence Expiry Date <span className="text-red-500">*</span></label>
          <input type="date" {...register('license_expiry_date')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          {errors.license_expiry_date && <p className="text-red-500 text-xs mt-1">{errors.license_expiry_date.message}</p>}
          {isExpired && (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-3 py-2 rounded-lg text-sm mt-2">
              ⚠ This licence has expired. Your application may be flagged for review.
            </div>
          )}
        </div>

        <div className="flex justify-between pt-4">
          <button type="button" onClick={() => navigate('/onboarding/contact')}
            className="border border-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-50 transition-colors">← Back</button>
          <button type="submit" disabled={isSubmitting}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium px-6 py-2 rounded-lg transition-colors">
            {isSubmitting ? 'Saving...' : 'Next →'}
          </button>
        </div>
      </form>
    </div>
  )
}
