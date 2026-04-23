import { defineNuxtPlugin } from '#app'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js'
import { Bar, Line } from 'vue-chartjs'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement)

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.component('BarChart', Bar)
  nuxtApp.vueApp.component('LineChart', Line)
})