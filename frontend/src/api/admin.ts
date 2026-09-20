import apiClient from './client'

export const getStatistics = () => apiClient.get('/api/admin/statistics/')

export const listApplications = (params?: {
  status?: string; search?: string; page?: number; page_size?: number
}) => apiClient.get('/api/admin/applications/', { params })

export const getApplication = (id: string) =>
  apiClient.get(`/api/admin/applications/${id}/`)

export const approveApplication = (id: string, note?: string) =>
  apiClient.post(`/api/admin/applications/${id}/approve/`, { note: note || '' })

export const rejectApplication = (id: string, reason: string) =>
  apiClient.post(`/api/admin/applications/${id}/reject/`, { reason })
