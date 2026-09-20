import apiClient from './client'

export const getProfile = () => apiClient.get('/api/driver/profile/')
export const updateProfile = (data: Record<string, unknown>) => apiClient.put('/api/driver/profile/', data)
export const getIdentity = () => apiClient.get('/api/driver/identity/')
export const updateIdentity = (data: Record<string, unknown>) => apiClient.put('/api/driver/identity/', data)
export const getVehicle = () => apiClient.get('/api/driver/vehicle/')
export const updateVehicle = (data: Record<string, unknown>) => apiClient.put('/api/driver/vehicle/', data)
export const getMyApplication = () => apiClient.get('/api/applications/me/')
export const createApplication = () => apiClient.post('/api/applications/')
export const submitApplication = (id: string) => apiClient.post(`/api/applications/${id}/submit/`)
export const getApplicationStatus = (id: string) => apiClient.get(`/api/applications/${id}/status/`)
