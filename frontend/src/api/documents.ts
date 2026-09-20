import apiClient from './client'

export const listDocuments = () => apiClient.get('/api/driver/documents/')

export const uploadDocument = (documentType: string, file: File) => {
  const formData = new FormData()
  formData.append('document_type', documentType)
  formData.append('file', file)
  return apiClient.post('/api/driver/documents/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const deleteDocument = (id: string) =>
  apiClient.delete(`/api/driver/documents/${id}/`)
