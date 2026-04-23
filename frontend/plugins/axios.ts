import { defineNuxtPlugin } from '#app'
import axios from 'axios'

export default defineNuxtPlugin((nuxtApp) => {
  const api = axios.create({
    baseURL: nuxtApp.$config.public.apiBaseUrl,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  // Добавляем интерцептор для авторизации
  api.interceptors.request.use(
    (config) => {
      const authStore = useAuthStore()
      if (authStore.token) {
        config.headers.Authorization = `Bearer ${authStore.token}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

 // Добавляем интерцептор для обработки ошибок
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        // Токен истек, перенаправляем на страницу логина
        const router = useRouter()
        router.push('/login')
      }
      return Promise.reject(error)
    }
  )

 nuxtApp.provide('axios', api)
})