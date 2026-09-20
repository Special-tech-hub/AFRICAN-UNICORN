import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface PersonalData {
  first_name: string; middle_name?: string; last_name: string
  date_of_birth: string; gender: string; nationality: string
}
interface ContactData {
  email: string; street_address: string; city: string; province: string
  emergency_contact_name: string; emergency_contact_phone: string
}
interface IdentityData {
  id_type: string; id_number: string
  drivers_license_number: string; license_expiry_date: string
}
interface VehicleData {
  vehicle_type: string; make: string; model: string
  year: number; registration_number: string; colour: string
}

interface OnboardingState {
  currentStep: number
  applicationId: string | null
  personal: PersonalData | null
  contact: ContactData | null
  identity: IdentityData | null
  vehicle: VehicleData | null
  setStep: (step: number) => void
  setApplicationId: (id: string) => void
  savePersonal: (data: PersonalData) => void
  saveContact: (data: ContactData) => void
  saveIdentity: (data: IdentityData) => void
  saveVehicle: (data: VehicleData) => void
  reset: () => void
}

export const useOnboardingStore = create<OnboardingState>()(
  persist(
    (set) => ({
      currentStep: 1,
      applicationId: null,
      personal: null,
      contact: null,
      identity: null,
      vehicle: null,
      setStep: (step) => set({ currentStep: step }),
      setApplicationId: (id) => set({ applicationId: id }),
      savePersonal: (data) => set({ personal: data }),
      saveContact: (data) => set({ contact: data }),
      saveIdentity: (data) => set({ identity: data }),
      saveVehicle: (data) => set({ vehicle: data }),
      reset: () => set({ currentStep: 1, applicationId: null, personal: null, contact: null, identity: null, vehicle: null }),
    }),
    { name: 'onboarding-storage', storage: createJSONStorage(() => sessionStorage) }
  )
)
