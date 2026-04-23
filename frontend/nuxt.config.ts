import { defineNuxtConfig } from 'nuxt/config'

export default defineNuxtConfig({
  // Настройки приложения
  app: {
    head: {
      title: 'AgroSeed AI',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { hid: 'description', name: 'description', content: 'Система прогнозирования изменения цен сельхоз-семян' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },

  // Модули
  modules: [
    '@pinia/nuxt'
  ],

  // Конфигурация runtime
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000/api/v1'
    }
  },

  // Плагины
  plugins: [
    '~/plugins/chart.client.ts'
  ],

  // Настройки сборки
  build: {
    transpile: ['chart.js']
  },

  // Настройки devtools
  devtools: { enabled: true }
})