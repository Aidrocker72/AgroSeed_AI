export const useApi = () => {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()

  return $fetch.create({
    baseURL: config.public.apiBaseUrl,
    onRequest({ options }) {
      const token = authStore.token
      if (token) {
        options.headers = {
          ...options.headers as Record<string, string>,
          Authorization: `Bearer ${token}`,
        }
      }
    },
    onResponseError({ response }) {
      if (response.status === 401) {
        authStore.$patch({ token: null, isAuthenticated: false, user: null })
        navigateTo('/login')
      }
    },
  })
}
