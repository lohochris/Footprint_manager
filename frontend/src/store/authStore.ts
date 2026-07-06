import { create } from 'zustand'

interface AuthState {
  token: string | null
  user: any | null
  login: (token: string, user: any) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  login: (token, user) => set(() => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    return { token, user }
  }),
  logout: () => set(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    return { token: null, user: null }
  }),
}))
