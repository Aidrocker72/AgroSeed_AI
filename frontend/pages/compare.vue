<template>
  <div class="compare-page">
    <h1>Сравнение культур</h1>

    <div class="card controls">
      <div class="controls-row">
        <div class="form-group">
          <label>Регион</label>
          <select v-model="selectedTerritory">
            <option value="">Выберите регион</option>
            <option v-for="t in territories" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
        </div>

        <div class="form-group">
          <label>Период прогноза</label>
          <div class="period-buttons">
            <button
              v-for="p in periods"
              :key="p.value"
              type="button"
              class="period-btn"
              :class="{ active: selectedPeriod === p.value }"
              @click="selectedPeriod = p.value"
            >{{ p.label }}</button>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label>Культуры</label>
        <div class="crop-checks">
          <label v-for="crop in crops" :key="crop.name" class="crop-check">
            <input type="checkbox" v-model="selectedCrops" :value="crop.name" />
            <span class="crop-dot" :style="{ background: crop.color }"></span>
            {{ crop.name }}
          </label>
        </div>
      </div>

      <div class="controls-bottom">
        <button
          class="btn-compare"
          :disabled="isRunning || !selectedTerritory || !selectedCrops.length"
          @click="runComparison"
        >
          {{ isRunning ? `Анализ ${progressLabel}` : 'Сравнить' }}
        </button>
        <div v-if="isRunning" class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPct + '%' }"></div>
        </div>
      </div>

      <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
    </div>

    <template v-if="results.length">
      <div class="card">
        <div class="chart-header">
          <h2>Динамика прогноза (₽)</h2>
          <div class="legend">
            <span v-for="r in results" :key="r.crop" class="legend-item">
              <span class="legend-dot" :style="{ background: colorOf(r.crop) }"></span>
              {{ r.crop }}
            </span>
          </div>
        </div>
        <div class="chart-wrap">
          <LineChart v-if="chartData" :data="chartData" :options="chartOptions" />
        </div>
      </div>

      <div class="card">
        <div class="table-top">
          <h2>Итоговая сводка</h2>
          <button class="export-btn" @click="exportCsv">⬇ Скачать CSV</button>
        </div>
        <table class="summary-table">
          <thead>
            <tr>
              <th>Культура</th>
              <th>Последняя цена</th>
              <th>Прогноз</th>
              <th>Изменение</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in results" :key="r.crop">
              <td>
                <span class="legend-dot" :style="{ background: colorOf(r.crop) }"></span>
                {{ r.crop }}
              </td>
              <td>{{ formatPrice(r.lastKnownPrice) }}</td>
              <td>{{ formatPrice(r.lastForecastPrice) }}</td>
              <td :class="r.change >= 0 ? 'positive' : 'negative'">
                {{ r.change >= 0 ? '+' : '' }}{{ r.change.toFixed(1) }}%
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const forecastStore = useForecastStore()
const { territories } = storeToRefs(forecastStore)

const crops = [
  { name: 'Пшеница',     color: '#f59e0b' },
  { name: 'Кукуруза',    color: '#f97316' },
  { name: 'Соя',         color: '#22c55e' },
  { name: 'Подсолнечник',color: '#8b5cf6' },
  { name: 'Ячмень',      color: '#3b82f6' },
]

const periods = [
  { label: '7 дней',  value: 7  },
  { label: '14 дней', value: 14 },
  { label: '30 дней', value: 30 },
  { label: '90 дней', value: 90 },
]

const selectedTerritory = ref('')
const selectedCrops = ref<string[]>(['Пшеница', 'Кукуруза', 'Соя'])
const selectedPeriod = ref(30)

const isRunning = ref(false)
const progressStep = ref(0)
const progressTotal = ref(0)
const errorMsg = ref('')

interface CropResult {
  crop: string
  forecast: { date: string; predicted_price: number }[]
  lastKnownPrice: number
  lastForecastPrice: number
  change: number
}
const results = ref<CropResult[]>([])

const progressPct = computed(() =>
  progressTotal.value ? Math.round((progressStep.value / progressTotal.value) * 100) : 0
)
const progressLabel = computed(() =>
  progressTotal.value ? `${progressStep.value}/${progressTotal.value}` : ''
)

onMounted(async () => {
  if (!territories.value.length) await forecastStore.fetchTerritories()
})

const colorOf = (cropName: string) =>
  crops.find(c => c.name === cropName)?.color ?? '#999'

const runComparison = async () => {
  if (!selectedTerritory.value || !selectedCrops.value.length) return

  isRunning.value = true
  errorMsg.value = ''
  results.value = []
  progressStep.value = 0
  progressTotal.value = selectedCrops.value.length

  const collected: CropResult[] = []

  for (const cropName of selectedCrops.value) {
    try {
      const data = await forecastStore.runForecastForCrop(
        Number(selectedTerritory.value),
        cropName,
        selectedPeriod.value,
      )
      const forecast = data.ai_result?.forecast ?? []
      const lastKnownPrice = data.ai_result?.model_info?.last_known_price ?? 0
      const lastForecastPrice = forecast[forecast.length - 1]?.predicted_price ?? 0
      const change = lastKnownPrice
        ? ((lastForecastPrice - lastKnownPrice) / lastKnownPrice) * 100
        : 0
      collected.push({ crop: cropName, forecast, lastKnownPrice, lastForecastPrice, change })
    } catch (e: any) {
      errorMsg.value = `Ошибка по культуре "${cropName}": ${e.data?.detail || e.message}`
    }
    progressStep.value++
  }

  results.value = collected
  isRunning.value = false
}

const chartData = computed(() => {
  if (!results.value.length) return null

  const labels = results.value[0].forecast.map((f: any) => f.date)

  return {
    labels,
    datasets: results.value.map(r => ({
      label: r.crop,
      data: r.forecast.map((f: any) => f.predicted_price),
      borderColor: colorOf(r.crop),
      backgroundColor: colorOf(r.crop) + '18',
      tension: 0.4,
      pointRadius: 1,
      fill: false,
    })),
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx: any) =>
          `${ctx.dataset.label}: ${new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', minimumFractionDigits: 0 }).format(ctx.parsed.y)}`,
      },
    },
  },
  scales: { y: { beginAtZero: false } },
}

const formatPrice = (price: number) =>
  price
    ? new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', minimumFractionDigits: 0 }).format(price)
    : '—'

const exportCsv = () => {
  if (!results.value.length) return

  const territory = territories.value.find((t: any) => t.id === Number(selectedTerritory.value))?.name ?? ''
  const dates = results.value[0].forecast.map((f: any) => f.date)

  const cropNames = results.value.map(r => r.crop)
  const header = ['Дата', ...cropNames]
  const rows = dates.map((date, i) => [
    date,
    ...results.value.map(r => r.forecast[i]?.predicted_price ?? ''),
  ])

  const csv = [header, ...rows].map(r => r.join(';')).join('\n')
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `agroseed_compare_${territory}_${selectedPeriod.value}d.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.compare-page {
  padding: 1.5rem 2rem;
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

h1 { font-size: 1.5rem; margin-bottom: 0; }

.card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.controls-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.form-group { display: flex; flex-direction: column; gap: 0.4rem; }

label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #444;
}

select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.95rem;
}

.period-buttons { display: flex; gap: 0.4rem; }

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

.crop-checks {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.crop-check {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.9rem;
  cursor: pointer;
  font-weight: 400;
  padding: 0.3rem 0.7rem;
  border: 1px solid #e5e5e5;
  border-radius: 20px;
  transition: background 0.15s;
}

.crop-check:hover { background: #f5f5f5; }

.crop-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.controls-bottom {
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-compare {
  padding: 0.55rem 1.5rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}

.btn-compare:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #e5e5e5;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #007bff;
  transition: width 0.3s ease;
}

.error-msg {
  margin-top: 0.75rem;
  padding: 0.6rem 0.8rem;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
  color: #856404;
  font-size: 0.9rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.chart-header h2 { margin: 0; font-size: 1rem; }

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.85rem;
  color: #444;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  display: inline-block;
}

.chart-wrap { height: 280px; }

.table-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.table-top h2 { margin: 0; font-size: 1rem; }

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

.export-btn:hover { background: #28a745; color: white; }

.summary-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.summary-table th {
  text-align: left;
  padding: 0.5rem 0.75rem;
  background: #f8f9fa;
  color: #555;
  font-weight: 600;
  border-bottom: 1px solid #eee;
}

.summary-table td {
  padding: 0.6rem 0.75rem;
  border-bottom: 1px solid #f5f5f5;
  vertical-align: middle;
}

.summary-table tr:last-child td { border-bottom: none; }

.summary-table td:first-child {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.positive { color: #22c55e; font-weight: 600; }
.negative { color: #ef4444; font-weight: 600; }
</style>
