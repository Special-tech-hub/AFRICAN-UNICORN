// TypeScript types for TakeOFF Driver Onboarding Platform
// Detailed types implemented in Tasks 11.x - 14.x

export interface User {
  id: string
  phone_number: string
  email: string | null
  role: 'DRIVER' | 'ADMIN'
  is_phone_verified: boolean
}

export interface AuthTokens {
  access: string
  refresh: string
}

export type ApplicationStatus = 'DRAFT' | 'SUBMITTED' | 'UNDER_REVIEW' | 'APPROVED' | 'REJECTED'

export interface Application {
  id: string
  application_reference: string
  status: ApplicationStatus
  submitted_at: string | null
  reviewed_at: string | null
  review_note: string | null
}

export interface StatusHistoryItem {
  previous_status: ApplicationStatus | null
  new_status: ApplicationStatus
  changed_by_role: string
  note: string | null
  created_at: string
}

export interface Document {
  id: string
  document_type: string
  original_filename: string
  file_size: number
  mime_type: string
  verification_status: string
  uploaded_at: string
  download_url: string
}

export interface Notification {
  id: string
  notification_type: string
  title: string
  message: string
  is_read: boolean
  created_at: string
}
