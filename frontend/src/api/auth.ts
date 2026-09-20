import apiClient from './client'
import type { AuthTokens, User } from '../types'

export const register = (data: { phone_number: string; password: string; confirm_password: string }) =>
  apiClient.post('/api/auth/register/', data)

export const verifyOtp = (data: { phone_number: string; otp: string }) =>
  apiClient.post<{ access: string; refresh: string; user: User }>('/api/auth/verify-otp/', data)

export const resendOtp = (data: { phone_number: string }) =>
  apiClient.post('/api/auth/resend-otp/', data)

export const login = (data: { phone_number: string; password: string }) =>
  apiClient.post<{ access: string; refresh: string; user: User }>('/api/auth/login/', data)

export const logout = (refresh: string) =>
  apiClient.post('/api/auth/logout/', { refresh })

export const refreshToken = (refresh: string) =>
  apiClient.post<AuthTokens>('/api/auth/refresh/', { refresh })
