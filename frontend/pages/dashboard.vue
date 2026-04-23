<template>
  <div class="dashboard">
    <h1>Панель управления</h1>
    
    <div class="dashboard-content">
      <div class="card">
        <h2>Создать новый прогноз</h2>
        <form @submit.prevent="createForecast">
          <div class="form-group">
            <label for="territory">Выберите территорию:</label>
            <select v-model="selectedTerritory" id="territory" required>
              <option value="">Выберите территорию</option>
              <option v-for="territory in territories" :key="territory.id" :value="territory.id">
                {{ territory.name }}
              </option>
            </select>
          </div>
          <button type="submit" :disabled="loading" class="btn btn-primary">
            {{ loading ? 'Создание...' : 'Создать прогноз' }}
          </button>
        </form>
      </div>

      <div class="card">
        <h2>Мои прогнозы</h2>
        <div v-if="forecasts.length === 0" class="no-data">
          У вас пока нет прогнозов
        </div>
        <div v-else class="forecasts-list">
          <div v-for="forecast in forecasts" :key="forecast.id" class="forecast-item">
            <div class="forecast-info">
              <h3>{{ getTerritoryName(forecast.territory_id) }}</h3>
              <p>Создан: {{ formatDate(forecast.created_at) }}</p>
            </div>
            <NuxtLink :to="`/forecast/${forecast.id}`" class="btn btn-secondary">
              Посмотреть
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const forecastStore = useForecastStore()
const { forecasts, territories, loading } = storeToRefs(forecastStore)

const selectedTerritory = ref('')

onMounted(async () => {
  await forecastStore.fetchTerritories()
  await forecastStore.fetchForecasts()
})

const createForecast = async () => {
  if (!selectedTerritory.value) return

  try {
    await forecastStore.createForecast(Number(selectedTerritory.value))
    selectedTerritory.value = ''
    await forecastStore.fetchForecasts()
  } catch (error) {
    console.error('Error creating forecast:', error)
  }
}

const getTerritoryName = (territoryId: number) => {
  const territory = territories.value.find((t: { id: number; name: string }) => t.id === territoryId)
  return territory ? territory.name : 'Неизвестная территория'
}

const formatDate = (dateString: string) => {
  const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'long', day: 'numeric' }
  return new Date(dateString).toLocaleDateString('ru-RU', options)
}
</script>

<style scoped>
.dashboard {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-content {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
  margin-top: 2rem;
}

.card {
  background: white;
  padding: 1.5rem;
 border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

select {
  width: 100%;
  padding: 0.5rem;
 border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.btn {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  text-decoration: none;
  font-weight: bold;
  cursor: pointer;
  border: none;
  font-size: 1rem;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.forecasts-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.forecast-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 4px;
}

.forecast-info h3 {
  margin: 0 0.5rem 0;
}

.forecast-info p {
  margin: 0;
  color: #666;
}

.no-data {
  text-align: center;
  color: #666;
  padding: 2rem;
}
</style>