import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as any,
    token: null as string | null,
    isAuthenticated: false,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    currentUser: (state) => state.user,
  },

  actions: {
    async login(email: string, password: string) {
      try {
        const response = await $fetch('/auth/login', {
          method: 'POST',
          body: { email, password }
        })

        this.token = response.access_token
        this.isAuthenticated = true
        
        // Установка заголовка авторизации для последующих запросов
        if (process.client) {
          (window as any).$nuxt.$axios.setHeader('Authorization', `Bearer ${this.token}`)
        }
        
        return response
      } catch (error) {
        console.error('Login error:', error)
        throw error
      }
    },

    async register(email: string, password: string, name?: string) {
      try {
        const response = await $fetch('/auth/register', {
          method: 'POST',
          body: { email, password, name }
        })

        return response
      } catch (error) {
        console.error('Registration error:', error)
        throw error
      }
    },

    async logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      
      if (process.client) {
        (window as any).$nuxt.$axios.setHeader('Authorization', null)
      }
    },

    async fetchUser() {
      if (!this.token) return null

      try {
        const response = await $fetch('/users/me', {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        })

        this.user = response
        return response
      } catch (error) {
        console.error('Error fetching user:', error)
        this.logout()
        throw error
      }
    }
  },

  // Сохранение состояния в localStorage
  persist: {
    key: 'auth',
    storage: localStorage,
    paths: ['token', 'isAuthenticated']
  }
})