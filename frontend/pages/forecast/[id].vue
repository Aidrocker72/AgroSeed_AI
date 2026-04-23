<template>
  <div class="forecast-detail">
    <div v-if="loading" class="loading">
      Загрузка...
    </div>
    <div v-else-if="currentForecast" class="forecast-content">
      <div class="forecast-header">
        <h1>Детали прогноза #{{ currentForecast.id }}</h1>
        <p>Территория: {{ getTerritoryName(currentForecast.territory_id) }}</p>
        <p>Дата создания: {{ formatDate(currentForecast.created_at) }}</p>
      </div>

      <div class="forecast-chart">
        <h2>График прогноза</h2>
        <!-- Здесь будет отображаться график с использованием Chart.js -->
        <LineChart 
          v-if="chartData" 
          :data="chartData" 
          :options="chartOptions"
          :height="400"
        />
      </div>

      <div class="forecast-details">
        <h2>Детали прогноза</h2>
        <div class="details-grid">
          <div class="detail-card">
            <h3>Период прогноза</h3>
            <p>30 дней</p>
          </div>
          <div class="detail-card">
            <h3>Метод прогнозирования</h3>
            <p>Random Forest + Prophet</p>
          </div>
          <div class="detail-card">
            <h3>Точность модели</h3>
            <p>MAE: {{ currentForecast.ai_result.model_info.mae?.toFixed(2) || 'N/A' }}</p>
          </div>
        </div>
      </div>

      <div class="forecast-data">
        <h2>Прогнозируемые данные</h2>
        <div class="data-table">
          <div class="table-header">
            <div class="col-date">Дата</div>
            <div class="col-price">Прогнозируемая цена</div>
            <div class="col-change">Изменение</div>
          </div>
          <div 
            v-for="(item, index) in currentForecast.ai_result.forecast" 
            :key="index" 
            class="table-row"
          >
            <div class="col-date">{{ formatDate(item.date) }}</div>
            <div class="col-price">{{ formatPrice(item.predicted_price) }}</div>
            <div class="col-change" :class="getChangeClass(item, index)">
              {{ getChangeValue(item, index) }}
            </div>
          </div>
        </div>
      </div>
    <div v-else class="error">
      Прогноз не найден
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const route = useRoute()
const forecastStore = useForecastStore()
const { currentForecast, loading } = storeToRefs(forecastStore)

// Получаем ID прогноза из параметров маршрута
const forecastId = computed(() => parseInt(route.params.id as string))

// Загружаем детали прогноза при монтировании компонента
onMounted(async () => {
 await forecastStore.fetchForecastById(forecastId.value)
})

// Обновляем данные при изменении ID прогноза
watch(forecastId, async (newId) => {
  if (newId) {
    await forecastStore.fetchForecastById(newId)
  }
})

// Подготовка данных для графика
const chartData = computed(() => {
  if (!currentForecast.value) return null
  
  const forecast = currentForecast.value.ai_result.forecast
  return {
    labels: forecast.map(item => formatDate(item.date)),
    datasets: [
      {
        label: 'Прогнозируемая цена',
        data: forecast.map(item => item.predicted_price),
        borderColor: '#007bff',
        backgroundColor: 'rgba(0, 123, 255, 0.1)',
        tension: 0.4
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: false
    }
 }
}

// Вспомогательные функции
const getTerritoryName = (territoryId: number) => {
  // В реальном приложении нужно получить название территории из хранилища
 return `Территория ${territoryId}`
}

const formatDate = (dateString: string) => {
  const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'short', day: 'numeric' }
  return new Date(dateString).toLocaleDateString('ru-RU', options)
}

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0
  }).format(price)
}

const getChangeValue = (item: any, index: number) => {
  if (index === 0) return '—'
  
  const prevItem = currentForecast.value?.ai_result.forecast[index - 1]
  if (!prevItem) return '—'
  
  const change = ((item.predicted_price - prevItem.predicted_price) / prevItem.predicted_price) * 100
  return `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`
}

const getChangeClass = (item: any, index: number) => {
  if (index === 0) return ''
  
  const prevItem = currentForecast.value?.ai_result.forecast[index - 1]
  if (!prevItem) return ''
  
  const change = item.predicted_price - prevItem.predicted_price
  return change >= 0 ? 'positive' : 'negative'
}
</script>

<style scoped>
.forecast-detail {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
}

.forecast-header {
  margin-bottom: 2rem;
}

.forecast-header h1 {
  margin-bottom: 0.5rem;
}

.forecast-chart {
  margin: 2rem 0;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.forecast-details {
  margin: 2rem 0;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.detail-card {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.detail-card h3 {
  margin-top: 0;
  color: #666;
}

.forecast-data {
  margin: 2rem 0;
}

.data-table {
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
 background-color: #f8f9fa;
  font-weight: bold;
  padding: 0.75rem;
  border-bottom: 1px solid #ddd;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  padding: 0.75rem;
  border-bottom: 1px solid #eee;
}

.table-row:last-child {
  border-bottom: none;
}

.col-date {
  font-weight: bold;
}

.col-price {
  color: #007bff;
  font-weight: bold;
}

.col-change.positive {
 color: #28a745;
}

.col-change.negative {
  color: #dc3545;
}
</style>