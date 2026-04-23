<template>
  <div class="home-page">
    <header class="hero-section">
      <div class="container">
        <h1>Добро пожаловать в AgroSeed AI</h1>
        <p>Система прогнозирования изменения цен сельхоз-семян</p>
        <div class="cta-buttons">
          <NuxtLink to="/login" class="btn btn-primary">Войти</NuxtLink>
          <NuxtLink to="/register" class="btn btn-secondary">Регистрация</NuxtLink>
        </div>
      </div>
    </header>

    <section class="features-section">
      <div class="container">
        <h2>Возможности системы</h2>
        <div class="features-grid">
          <div class="feature-card">
            <h3>📊 Прогнозирование цен</h3>
            <p>Точное предсказание изменения цен на сельхоз-семена с использованием машинного обучения</p>
          </div>
          <div class="feature-card">
            <h3>🌍 Анализ территорий</h3>
            <p>Прогнозы для различных географических регионов с учетом местных факторов</p>
          </div>
          <div class="feature-card">
            <h3>📰 Анализ новостей</h3>
            <p>Учет влияния новостей и событий на цены на семена</p>
          </div>
        </div>
      </div>
    </section>

    <section class="how-it-works">
      <div class="container">
        <h2>Как это работает</h2>
        <div class="steps">
          <div class="step">
            <div class="step-number">1</div>
            <h3>Сбор данных</h3>
            <p>Наши системы собирают актуальные данные о ценах на семена и相关新闻</p>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <h3>Анализ</h3>
            <p>Машинное обучение анализирует данные и выявляет закономерности</p>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <h3>Прогноз</h3>
            <p>Получите точный прогноз изменения цен на выбранный период</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default'
})

useHead({
  title: 'AgroSeed AI - Система прогнозирования изменения цен сельхоз-семян',
  meta: [
    { name: 'description', content: 'Точное прогнозирование цен на сельхоз-семена с использованием машинного обучения' }
  ]
})
</script>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, #6a93cb 0%, #a4bfef 100%);
  color: white;
  padding: 4rem 0;
  text-align: center;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
}

.cta-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  text-decoration: none;
  font-weight: bold;
  transition: opacity 0.3s;
}

.btn:hover {
  opacity: 0.9;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-secondary {
  background-color: white;
  color: #007bff;
}

.features-section {
  padding: 4rem 0;
  background-color: #f8f9fa;
}

.features-section h2 {
  text-align: center;
  margin-bottom: 3rem;
  font-size: 2rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
 max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.feature-card h3 {
  margin-bottom: 1rem;
  color: #007bff;
}

.how-it-works {
  padding: 4rem 0;
}

.how-it-works h2 {
  text-align: center;
  margin-bottom: 3rem;
  font-size: 2rem;
}

.steps {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.step {
  flex: 1;
  min-width: 250px;
  text-align: center;
  padding: 1rem;
}

.step-number {
  width: 50px;
  height: 50px;
  background-color: #007bff;
  color: white;
  border-radius: 50%;
  display: flex;
 align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  font-size: 1.5rem;
  font-weight: bold;
}
</style>