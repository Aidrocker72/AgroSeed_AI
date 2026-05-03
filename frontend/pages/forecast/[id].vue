<template>
  <div class="forecast-detail">
    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else-if="currentForecast" class="forecast-content">
      <div class="forecast-header">
        <NuxtLink to="/dashboard" class="back-link">← Назад</NuxtLink>
        <h1>{{ getTerritoryName(currentForecast.territory_id) }}</h1>
        <div class="header-tags">
          <span class="tag tag-crop">{{ currentForecast.raw_data?.crop_name || 'Культура не указана' }}</span>
          <span class="tag tag-period">{{ currentForecast.raw_data?.forecast_period || 30 }} дней</span>
          <span class="tag tag-date">{{ formatDate(currentForecast.created_at) }}</span>
        </div>
      </div>

      <div class="two-col">
        <!-- График -->
        <div class="card chart-card">
          <h2>График прогноза цен</h2>
          <div class="chart-wrap">
            <LineChart
              v-if="chartData"
              :data="chartData"
              :options="chartOptions"
            />
          </div>
        </div>

        <!-- Сводка -->
        <div class="sidebar">
          <div class="card stat-card">
            <div class="stat-label">Последняя цена</div>
            <div class="stat-value">{{ formatPrice(currentForecast.ai_result?.model_info?.last_known_price) }}</div>
            <div class="stat-sub">{{ currentForecast.ai_result?.model_info?.last_known_date }}</div>
          </div>
          <div class="card stat-card">
            <div class="stat-label">Прогноз на {{ currentForecast.raw_data?.forecast_period || 30 }} дней</div>
            <div class="stat-value">{{ formatPrice(lastForecastPrice) }}</div>
            <div class="stat-sub" :class="trendClass">{{ trendLabel }}</div>
          </div>
          <div class="card stat-card">
            <div class="stat-label">Модель</div>
            <div class="stat-value model-name">{{ currentForecast.ai_result?.model_info?.model_type || 'RF + HW' }}</div>
          </div>
        </div>
      </div>

      <!-- Таблица -->
      <div class="card">
        <div class="table-top">
          <h2>Прогнозируемые данные</h2>
          <button class="export-btn" @click="exportCsv">⬇ Скачать CSV</button>
        </div>
        <div class="data-table">
          <div class="table-header">
            <div>Дата</div>
            <div>Цена (₽)</div>
            <div>Изменение</div>
          </div>
          <div
            v-for="(item, index) in currentForecast.ai_result.forecast"
            :key="index"
            class="table-row"
          >
            <div>{{ formatDate(item.date) }}</div>
            <div class="col-price">{{ formatPrice(item.predicted_price) }}</div>
            <div :class="getChangeClass(item, index)">{{ getChangeValue(item, index) }}</div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="error">Прогноз не найден</div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const route = useRoute()
const forecastStore = useForecastStore()
const { currentForecast, loading, territories } = storeToRefs(forecastStore)

const forecastId = computed(() => parseInt(route.params.id as string))

onMounted(async () => {
  if (!territories.value.length) await forecastStore.fetchTerritories()
  await forecastStore.fetchForecastById(forecastId.value)
})

watch(forecastId, async (id: number) => {
  if (id) await forecastStore.fetchForecastById(id)
})

const chartData = computed(() => {
  if (!currentForecast.value) return null
  const forecast = currentForecast.value.ai_result.forecast
  const ci = currentForecast.value.ai_result.confidence_interval
  return {
    labels: forecast.map((item: any) => item.date),
    datasets: [
      {
        label: 'Прогноз',
        data: forecast.map((item: any) => item.predicted_price),
        borderColor: '#007bff',
        backgroundColor: 'rgba(0, 123, 255, 0.08)',
        tension: 0.4,
        fill: false,
        pointRadius: 2,
      },
      ...(ci ? [{
        label: 'Верхняя граница',
        data: ci.upper_bound,
        borderColor: 'rgba(0,123,255,0.25)',
        backgroundColor: 'rgba(0,123,255,0.08)',
        borderDash: [4, 4],
        tension: 0.4,
        fill: '+1',
        pointRadius: 0,
      }, {
        label: 'Нижняя граница',
        data: ci.lower_bound,
        borderColor: 'rgba(0,123,255,0.25)',
        backgroundColor: 'rgba(0,123,255,0.08)',
        borderDash: [4, 4],
        tension: 0.4,
        fill: false,
        pointRadius: 0,
      }] : []),
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: { legend: { display: false } },
  scales: { y: { beginAtZero: false } },
}

const lastForecastPrice = computed(() => {
  const f = currentForecast.value?.ai_result?.forecast
  return f?.length ? f[f.length - 1].predicted_price : null
})

const trendClass = computed(() => {
  const last = lastForecastPrice.value
  const first = currentForecast.value?.ai_result?.model_info?.last_known_price
  if (!last || !first) return ''
  return last >= first ? 'positive' : 'negative'
})

const trendLabel = computed(() => {
  const last = lastForecastPrice.value
  const first = currentForecast.value?.ai_result?.model_info?.last_known_price
  if (!last || !first) return ''
  const pct = ((last - first) / first) * 100
  return `${pct >= 0 ? '+' : ''}${pct.toFixed(1)}% за период`
})

const getTerritoryName = (id: number) => {
  const t = territories.value.find((t: any) => t.id === id)
  return t ? t.name : `Территория ${id}`
}

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })

const formatPrice = (price: number) =>
  price != null
    ? new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', minimumFractionDigits: 0 }).format(price)
    : '—'

const getChangeValue = (item: any, index: number) => {
  if (index === 0) return '—'
  const prev = currentForecast.value?.ai_result.forecast[index - 1]
  if (!prev) return '—'
  const pct = ((item.predicted_price - prev.predicted_price) / prev.predicted_price) * 100
  return `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%`
}

const getChangeClass = (item: any, index: number) => {
  if (index === 0) return ''
  const prev = currentForecast.value?.ai_result.forecast[index - 1]
  if (!prev) return ''
  return item.predicted_price >= prev.predicted_price ? 'positive' : 'negative'
}

const exportCsv = () => {
  const f = currentForecast.value
  if (!f) return

  const forecast = f.ai_result.forecast
  const ci = f.ai_result.confidence_interval
  const territory = getTerritoryName(f.territory_id)
  const crop = f.raw_data?.crop_name || ''
  const period = f.raw_data?.forecast_period || 30

  const header = ['Дата', 'Прогноз (₽)', 'Нижняя граница (₽)', 'Верхняя граница (₽)', 'Изменение (%)']
  const rows = forecast.map((item: any, i: number) => {
    const prev = forecast[i - 1]
    const pct = prev ? (((item.predicted_price - prev.predicted_price) / prev.predicted_price) * 100).toFixed(2) : ''
    const lower = ci?.lower_bound?.[i] ?? ''
    const upper = ci?.upper_bound?.[i] ?? ''
    return [item.date, item.predicted_price, lower, upper, pct]
  })

  const csv = [header, ...rows].map(r => r.join(';')).join('\n')
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `agroseed_${territory}_${crop}_${period}d.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.forecast-detail {
  padding: 1.5rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
  font-size: 1.1rem;
  color: #666;
}

.back-link {
  display: inline-block;
  color: #007bff;
  text-decoration: none;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.forecast-header {
  margin-bottom: 1.5rem;
}

.forecast-header h1 {
  margin: 0.25rem 0 0.5rem;
  font-size: 1.6rem;
}

.header-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tag {
  font-size: 0.8rem;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-weight: 600;
}

.tag-crop  { background: #e8f4fd; color: #0066cc; }
.tag-period { background: #f0faf0; color: #2d862d; }
.tag-date  { background: #f5f5f5; color: #555; font-weight: 400; }

.two-col {
  display: grid;
  grid-template-columns: 1fr 220px;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  align-items: start;
}

.card {
  background: white;
  padding: 1.25rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.card h2 {
  margin: 0 0 1rem;
  font-size: 1rem;
  color: #333;
}

.chart-card { }

.chart-wrap {
  height: 240px;
  position: relative;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.stat-card {
  padding: 1rem;
}

.stat-label {
  font-size: 0.75rem;
  color: #888;
  margin-bottom: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.stat-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #222;
}

.model-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #555;
}

.stat-sub {
  font-size: 0.8rem;
  color: #888;
  margin-top: 0.15rem;
}

.stat-sub.positive { color: #28a745; }
.stat-sub.negative { color: #dc3545; }

.table-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.table-top h2 { margin: 0; }

.export-btn {
  padding: 0.35rem 0.9rem;
  border: 1px solid #28a745;
  border-radius: 4px;
  background: white;
  color: #28a745;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.export-btn:hover {
  background: #28a745;
  color: white;
}

.data-table {
  border: 1px solid #eee;
  border-radius: 6px;
  overflow: hidden;
  font-size: 0.9rem;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr;
  background: #f8f9fa;
  font-weight: 600;
  padding: 0.6rem 1rem;
  border-bottom: 1px solid #eee;
  color: #555;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid #f5f5f5;
}

.table-row:last-child { border-bottom: none; }

.col-price { color: #007bff; font-weight: 600; }

.positive { color: #28a745; }
.negative { color: #dc3545; }

@media (max-width: 768px) {
  .forecast-detail {
    padding: 1rem;
  }

  .two-col {
    grid-template-columns: 1fr;
  }

  .sidebar {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .stat-card {
    flex: 1 1 calc(50% - 0.375rem);
    min-width: 140px;
  }

  .forecast-header h1 {
    font-size: 1.3rem;
  }

  .table-header,
  .table-row {
    grid-template-columns: 1.5fr 1.2fr 1fr;
    font-size: 0.82rem;
    padding: 0.45rem 0.6rem;
  }

  .export-btn {
    font-size: 0.8rem;
    padding: 0.3rem 0.6rem;
  }
}

@media (max-width: 480px) {
  .sidebar {
    flex-direction: column;
  }

  .stat-card {
    flex: 1 1 100%;
  }
}
</style>
