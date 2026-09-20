import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { getProfile, updateProfile } from '../../api/onboarding'
import { useOnboardingStore } from '../../store/onboardingStore'

const schema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  middle_name: z.string().optional(),
  last_name: z.string().min(1, 'Last name is required'),
  date_of_birth: z.string().min(1, 'Date of birth is required'),
  gender: z.enum(['MALE','FEMALE','OTHER','PREFER_NOT_TO_SAY'], { errorMap: () => ({ message: 'Please select a gender' }) }),
  nationality: z.string().min(1, 'Nationality is required'),
})
type FormData = z.infer<typeof schema>

export default function PersonalDetailsStep() {
  const navigate = useNavigate()
  const { savePersonal } = useOnboardingStore()
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  useEffect(() => {
    getProfile().then((r) => { if (r.data.first_name) reset(r.data) }).catch(() => {})
  }, [reset])

  const onSubmit = async (data: FormData) => {
    await updateProfile(data)
    savePersonal(data)
    navigate('/onboarding/contact')
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm p-8">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Personal Details</h2>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">First Name <span className="text-red-500">*</span></label>
            <input {...register('first_name')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            {errors.first_name && <p className="text-red-500 text-xs mt-1">{errors.first_name.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Middle Name</label>
            <input {...register('middle_name')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Last Name <span className="text-red-500">*</span></label>
          <input {...register('last_name')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          {errors.last_name && <p className="text-red-500 text-xs mt-1">{errors.last_name.message}</p>}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth <span className="text-red-500">*</span></label>
            <input type="date" {...register('date_of_birth')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            {errors.date_of_birth && <p className="text-red-500 text-xs mt-1">{errors.date_of_birth.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Gender <span className="text-red-500">*</span></label>
            <select {...register('gender')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">Select...</option>
              <option value="MALE">Male</option>
              <option value="FEMALE">Female</option>
              <option value="OTHER">Other</option>
              <option value="PREFER_NOT_TO_SAY">Prefer not to say</option>
            </select>
            {errors.gender && <p className="text-red-500 text-xs mt-1">{errors.gender.message}</p>}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Nationality <span className="text-red-500">*</span></label>
          <input {...register('nationality')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          {errors.nationality && <p className="text-red-500 text-xs mt-1">{errors.nationality.message}</p>}
        </div>
        <div className="flex justify-end pt-4">
          <button type="submit" disabled={isSubmitting} className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium px-6 py-2 rounded-lg transition-colors">
            {isSubmitting ? 'Saving...' : 'Next →'}
          </button>
        </div>
      </form>
    </div>
  )
}
