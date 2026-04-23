import { defineStore } from 'pinia'

export const useForecastStore = defineStore('forecast', {
  state: () => ({
    forecasts: [] as any[],
    currentForecast: null as any,
    territories: [] as any[],
    loading: false,
    error: null as string | null,
  }),

  getters: {
    getForecasts: (state) => state.forecasts,
    getCurrentForecast: (state) => state.currentForecast,
    getTerritories: (state) => state.territories,
  },

  actions: {
    async fetchTerritories() {
      this.loading = true
      try {
        const response = await $fetch('/territories')
        this.territories = response
        this.error = null
      } catch (error) {
        console.error('Error fetching territories:', error)
        this.error = 'Ошибка загрузки территорий'
      } finally {
        this.loading = false
      }
    },

    async fetchForecasts() {
      this.loading = true
      try {
        const response = await $fetch('/forecast/list')
        this.forecasts = response
        this.error = null
      } catch (error) {
        console.error('Error fetching forecasts:', error)
        this.error = 'Ошибка загрузки прогнозов'
      } finally {
        this.loading = false
      }
    },

    async fetchForecastById(id: number) {
      this.loading = true
      try {
        const response = await $fetch(`/forecast/${id}`)
        this.currentForecast = response
        this.error = null
      } catch (error) {
        console.error('Error fetching forecast:', error)
        this.error = 'Ошибка загрузки прогноза'
      } finally {
        this.loading = false
      }
    },

    async createForecast(territoryId: number) {
      this.loading = true
      try {
        const response = await $fetch('/forecast/run', {
          method: 'POST',
          body: { territory_id: territoryId }
        })
        // Добавляем новый прогноз в список
        this.forecasts.unshift(response)
        this.currentForecast = response
        this.error = null
        return response
      } catch (error) {
        console.error('Error creating forecast:', error)
        this.error = 'Ошибка создания прогноза'
        throw error
      } finally {
        this.loading = false
      }
    }
 }
})