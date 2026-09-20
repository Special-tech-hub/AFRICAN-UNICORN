import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { getVehicle, updateVehicle } from '../../api/onboarding'

const currentYear = new Date().getFullYear()

const schema = z.object({
  vehicle_type: z.enum(['MOTORCYCLE','SEDAN','HATCHBACK','PICKUP','VAN','TRUCK'], {
    errorMap: () => ({ message: 'Select a vehicle type' }),
  }),
  make: z.string().min(1, 'Make is required'),
  model: z.string().min(1, 'Model is required'),
  year: z.coerce.number()
    .min(1900, 'Year cannot be before 1900')
    .max(currentYear + 1, `Year cannot be after ${currentYear + 1}`),
  registration_number: z.string().min(1, 'Registration number is required'),
  colour: z.string().min(1, 'Colour is required'),
})
type FormData = z.infer<typeof schema>

export default function VehicleDetailsStep() {
  const navigate = useNavigate()
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  useEffect(() => {
    getVehicle().then((r) => { if (r.data.make) reset(r.data) }).catch(() => {})
  }, [reset])

  const onSubmit = async (data: FormData) => {
    await updateVehicle(data)
    navigate('/onboarding/documents')
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm p-8">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Vehicle Details</h2>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Vehicle Type <span className="text-red-500">*</span></label>
          <select {...register('vehicle_type')} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">Select...</option>
            {['MOTORCYCLE','SEDAN','HATCHBACK','PICKUP','VAN','TRUCK'].map(t => (
              <option key={t} value={t}>{t.charAt(0) + t.slice(1).toLowerCase()}</option>
            ))}
          </select>
          {errors.vehicle_type && <p className="text-red-500 text-xs mt-1">{errors.vehicle_type.message}</p>}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Make <span className="text-red-500">*</span></label>
            <input {...register('make')} placeholder="e.g. Toyota" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            {errors.make && <p className="text-red-500 text-xs mt-1">{errors.make.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Model <span className="text-red-500">*</span></label>
            <input {...register('model')} placeholder="e.g. Corolla" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            {errors.model && <p className="text-red-500 text-xs mt-1">{errors.model.message}</p>}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Year <span className="text-red-500">*</span></label>
            <input type="number" {...register('year')} placeholder="e.g. 2020" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            {errors.year && <p className="text-red-500 text-xs mt-1">{errors.year.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Colour <span className="text-red-500">*</span></label>
            <input {...register('colour')} placeholder="e.g. White" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            {errors.colour && <p className="text-red-500 text-xs mt-1">{errors.colour.message}</p>}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Registration Number <span className="text-red-500">*</span></label>
          <input {...register('registration_number')} placeholder="e.g. TEST-1234" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          {errors.registration_number && <p className="text-red-500 text-xs mt-1">{errors.registration_number.message}</p>}
        </div>

        <div className="flex justify-between pt-4">
          <button type="button" onClick={() => navigate('/onboarding/identity')}
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
