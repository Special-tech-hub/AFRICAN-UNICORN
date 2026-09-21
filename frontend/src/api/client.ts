import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://african-unicorn.onrender.com'

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor: attach JWT access token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const stored = localStorage.getItem('auth-storage')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        const token = parsed?.state?.accessToken
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`
        }
      } catch {}
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: auto-refresh on 401
let isRefreshing = false
let failedQueue: Array<{ resolve: (v: string) => void; reject: (e: unknown) => void }> = []

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((p) => (error ? p.reject(error) : p.resolve(token!)))
  failedQueue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          original.headers.Authorization = `Bearer ${token}`
          return apiClient(original)
        })
      }
      original._retry = true
      isRefreshing = true

      try {
        const stored = localStorage.getItem('auth-storage')
        const refreshToken = stored ? JSON.parse(stored)?.state?.refreshToken : null
        if (!refreshToken) throw new Error('No refresh token')

        const { data } = await axios.post(`${API_BASE_URL}/api/auth/refresh/`, {
          refresh: refreshToken,
        })
        const newAccess = data.access

        // Update stored token
        const authStorage = JSON.parse(localStorage.getItem('auth-storage') || '{}')
        if (authStorage.state) authStorage.state.accessToken = newAccess
        localStorage.setItem('auth-storage', JSON.stringify(authStorage))

        processQueue(null, newAccess)
        original.headers.Authorization = `Bearer ${newAccess}`
        return apiClient(original)
      } catch (refreshError) {
        processQueue(refreshError, null)
        localStorage.removeItem('auth-storage')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
