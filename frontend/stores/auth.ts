import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', () => {
  const tokenCookie = useCookie<string | null>('auth_token', { maxAge: 60 * 60 * 24 })
  const token = ref<string | null>(tokenCookie.value ?? null)
  const user = ref<any>(null)
  const isAuthenticated = computed(() => !!token.value)

  const login = async (email: string, password: string) => {
    const config = useRuntimeConfig()
    const response = await $fetch<{ access_token: string }>('/auth/login', {
      baseURL: config.public.apiBaseUrl,
      method: 'POST',
      body: { email, password },
    })
    tokenCookie.value = response.access_token
    token.value = response.access_token
    return response
  }

  const register = async (email: string, password: string) => {
    const config = useRuntimeConfig()
    return await $fetch('/auth/register', {
      baseURL: config.public.apiBaseUrl,
      method: 'POST',
      body: { email, password },
    })
  }

  const logout = () => {
    tokenCookie.value = null
    token.value = null
    user.value = null
    navigateTo('/login')
  }

  const fetchUser = async () => {
    if (!token.value) return null
    try {
      const api = useApi()
      user.value = await api('/users/me')
      return user.value
    } catch {
      logout()
    }
  }

  return { token, user, isAuthenticated, login, register, logout, fetchUser }
})
