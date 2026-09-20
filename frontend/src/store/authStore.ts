import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, AuthTokens } from '../types'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  login: (tokens: AuthTokens, user: User) => void
  logout: () => void
  setTokens: (tokens: AuthTokens) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      login: (tokens, user) =>
        set({ user, accessToken: tokens.access, refreshToken: tokens.refresh }),
      logout: () => set({ user: null, accessToken: null, refreshToken: null }),
      setTokens: (tokens) =>
        set({ accessToken: tokens.access, refreshToken: tokens.refresh }),
    }),
    { name: 'auth-storage' }
  )
)
