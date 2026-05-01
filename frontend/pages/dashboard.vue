<template>
  <div class="dashboard">
    <h1>Панель управления</h1>

    <div class="dashboard-content">
      <div class="card">
        <h2>Создать новый прогноз</h2>
        <form @submit.prevent="createForecast">
          <div class="form-group">
            <label for="territory">Регион:</label>
            <select v-model="selectedTerritory" id="territory" required>
              <option value="">Выберите регион</option>
              <option v-for="t in territories" :key="t.id" :value="t.id">
                {{ t.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="crop">Культура:</label>
            <select v-model="selectedCrop" id="crop" required>
              <option v-for="c in crops" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>

          <div class="form-group">
            <label>Период прогноза:</label>
            <div class="period-buttons">
              <button
                v-for="p in periods"
                :key="p.value"
                type="button"
                class="period-btn"
                :class="{ active: selectedPeriod === p.value }"
                @click="selectedPeriod = p.value"
              >
                {{ p.label }}
              </button>
            </div>
          </div>

          <button type="submit" :disabled="loading || !selectedTerritory" class="btn btn-primary">
            {{ loading ? 'Создание...' : 'Создать прогноз' }}
          </button>
          <div v-if="error" class="error-message">{{ error }}</div>
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
              <div class="forecast-tags">
                <span class="tag tag-crop">{{ forecast.raw_data?.crop_name || '—' }}</span>
                <span class="tag tag-period">{{ forecast.raw_data?.forecast_period || 30 }} дней</span>
              </div>
              <p class="forecast-date">{{ formatDate(forecast.created_at) }}</p>
            </div>
            <NuxtLink :to="`/forecast/${forecast.id}`" class="btn btn-secondary">
              Открыть
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

const crops = ['Пшеница', 'Кукуруза', 'Соя', 'Подсолнечник', 'Ячмень']
const periods = [
  { label: '7 дней', value: 7 },
  { label: '14 дней', value: 14 },
  { label: '30 дней', value: 30 },
  { label: '90 дней', value: 90 },
]

const selectedTerritory = ref('')
const selectedCrop = ref('Пшеница')
const selectedPeriod = ref(30)

onMounted(async () => {
  await forecastStore.fetchTerritories()
  await forecastStore.fetchForecasts()
})

const createForecast = async () => {
  if (!selectedTerritory.value) return
  try {
    const forecast = await forecastStore.createForecast(
      Number(selectedTerritory.value),
      selectedCrop.value,
      selectedPeriod.value
    )
    selectedTerritory.value = ''
    await navigateTo(`/forecast/${forecast.id}`)
  } catch (error) {
    console.error('Error creating forecast:', error)
  }
}

const getTerritoryName = (territoryId: number) => {
  const t = territories.value.find((t: { id: number; name: string }) => t.id === territoryId)
  return t ? t.name : 'Неизвестный регион'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU', { year: 'numeric', month: 'short', day: 'numeric' })
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
  align-self: start;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.4rem;
  font-weight: 600;
  font-size: 0.9rem;
  color: #444;
}

select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 0.95rem;
}

.period-buttons {
  display: flex;
  gap: 0.5rem;
}

.period-btn {
  flex: 1;
  padding: 0.4rem 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.15s;
}

.period-btn.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
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
  width: 100%;
  margin-top: 0.5rem;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  white-space: nowrap;
}

.btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.forecasts-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.forecast-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.85rem 1rem;
  border: 1px solid #eee;
  border-radius: 6px;
}

.forecast-info h3 {
  margin: 0 0 0.3rem;
  font-size: 1rem;
}

.forecast-tags {
  display: flex;
  gap: 0.4rem;
  margin-bottom: 0.3rem;
}

.tag {
  font-size: 0.75rem;
  padding: 0.1rem 0.5rem;
  border-radius: 12px;
  font-weight: 600;
}

.tag-crop {
  background: #e8f4fd;
  color: #0066cc;
}

.tag-period {
  background: #f0faf0;
  color: #2d862d;
}

.forecast-date {
  margin: 0;
  color: #888;
  font-size: 0.82rem;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 2rem;
}

.error-message {
  margin-top: 0.75rem;
  padding: 0.6rem 0.8rem;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
  color: #856404;
  font-size: 0.9rem;
}
</style>
