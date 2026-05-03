import { defineStore } from 'pinia'

export const useForecastStore = defineStore('forecast', () => {
  const forecasts = ref<any[]>([])
  const currentForecast = ref<any>(null)
  const territories = ref<any[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchTerritories = async () => {
    loading.value = true
    try {
      const api = useApi()
      territories.value = await api('/territories')
      error.value = null
    } catch (e) {
      error.value = 'Ошибка загрузки территорий'
    } finally {
      loading.value = false
    }
  }

  const fetchForecasts = async () => {
    loading.value = true
    try {
      const api = useApi()
      forecasts.value = await api('/forecast/list')
      error.value = null
    } catch (e) {
      error.value = 'Ошибка загрузки прогнозов'
    } finally {
      loading.value = false
    }
  }

  const fetchForecastById = async (id: number) => {
    loading.value = true
    try {
      const api = useApi()
      currentForecast.value = await api(`/forecast/${id}`)
      error.value = null
    } catch (e) {
      error.value = 'Ошибка загрузки прогноза'
    } finally {
      loading.value = false
    }
  }

  const createForecast = async (territoryId: number, cropName: string, forecastPeriod: number) => {
    loading.value = true
    try {
      const api = useApi()
      const params = new URLSearchParams({
        territory_id: String(territoryId),
        crop_name: cropName,
        forecast_period: String(forecastPeriod),
      })
      const response = await api(`/forecast/run?${params}`, { method: 'POST' })
      forecasts.value.unshift(response)
      currentForecast.value = response
      error.value = null
      return response
    } catch (e: any) {
      error.value = e.data?.detail || e.message || 'Ошибка создания прогноза'
      throw e
    } finally {
      loading.value = false
    }
  }

  const runForecastForCrop = async (territoryId: number, cropName: string, forecastPeriod: number) => {
    const api = useApi()
    const params = new URLSearchParams({
      territory_id: String(territoryId),
      crop_name: cropName,
      forecast_period: String(forecastPeriod),
    })
    return await api(`/forecast/run?${params}`, { method: 'POST' })
  }

  const deleteForecast = async (id: number) => {
    const api = useApi()
    await api(`/forecast/${id}`, { method: 'DELETE' })
    forecasts.value = forecasts.value.filter((f: any) => f.id !== id)
  }

  return {
    forecasts,
    currentForecast,
    territories,
    loading,
    error,
    fetchTerritories,
    fetchForecasts,
    fetchForecastById,
    createForecast,
    runForecastForCrop,
    deleteForecast,
  }
})
