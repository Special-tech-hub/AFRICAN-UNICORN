import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { getProfile, updateProfile } from '../../api/onboarding'
import { useAuthStore } from '../../store/authStore'

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
  street_address: z.string().min(1, 'Street address is required'),
  city: z.string().min(1, 'City is required'),
  province: z.string().min(1, 'Province is required'),
  emergency_contact_name: z.string().min(1, 'Emergency contact name is required'),
  emergency_contact_phone: z.string().min(7, 'Enter a valid phone number'),
})
type FormData = z.infer<typeof schema>

export default function ContactDetailsStep() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  useEffect(() => {
    getProfile().then((r) => { if (r.data.email) reset(r.data) }).catch(() => {})
  }, [reset])

  const onSubmit = async (data: FormData) => {
    await updateProfile(data)
    navigate('/onboarding/identity')
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm p-8">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Contact Details</h2>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
          <input value={user?.phone_number || ''} disabled
            className="w-full border border-gray-200 bg-gray-50 rounded-lg px-3 py-2 text-sm text-gray-500 cursor-not-allowed" />
          <p className="text-xs text-gray-400 mt-1">Verified phone — cannot be changed here</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email Address <span className="text-red-500">*</span></label>
          <input type="email" {...register('email')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Street Address <span className="text-red-500">*</span></label>
          <input {...register('street_address')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          {errors.street_address && <p className="text-red-500 text-xs mt-1">{errors.street_address.message}</p>}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">City <span className="text-red-500">*</span></label>
            <input {...register('city')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            {errors.city && <p className="text-red-500 text-xs mt-1">{errors.city.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Province <span className="text-red-500">*</span></label>
            <input {...register('province')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            {errors.province && <p className="text-red-500 text-xs mt-1">{errors.province.message}</p>}
          </div>
        </div>

        <div className="border-t pt-4">
          <h3 className="text-sm font-semibold text-gray-800 mb-3">Emergency Contact</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name <span className="text-red-500">*</span></label>
              <input {...register('emergency_contact_name')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              {errors.emergency_contact_name && <p className="text-red-500 text-xs mt-1">{errors.emergency_contact_name.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone <span className="text-red-500">*</span></label>
              <input type="tel" {...register('emergency_contact_phone')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              {errors.emergency_contact_phone && <p className="text-red-500 text-xs mt-1">{errors.emergency_contact_phone.message}</p>}
            </div>
          </div>
        </div>

        <div className="flex justify-between pt-4">
          <button type="button" onClick={() => navigate('/onboarding/personal')}
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
