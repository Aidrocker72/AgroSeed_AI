<template>
  <div class="app-layout">
    <nav class="navbar" v-if="isAuthenticated">
      <NuxtLink to="/dashboard" class="nav-logo">🌾 AgroSeed AI</NuxtLink>
      <div class="nav-right">
        <NuxtLink to="/dashboard" class="nav-link">Прогнозы</NuxtLink>
        <NuxtLink to="/compare" class="nav-link">Сравнение</NuxtLink>
        <button class="logout-btn" @click="logout">Выйти</button>
      </div>
    </nav>
    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore()
const { isAuthenticated } = storeToRefs(authStore)

const logout = () => authStore.logout()
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f7fa; color: #222; }
</style>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  height: 56px;
  background: white;
  border-bottom: 1px solid #e8e8e8;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-logo {
  font-size: 1.1rem;
  font-weight: 700;
  color: #2d6a4f;
  text-decoration: none;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  color: #555;
  text-decoration: none;
  font-size: 0.9rem;
}

.nav-link:hover { color: #007bff; }

.logout-btn {
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.3rem 0.8rem;
  cursor: pointer;
  font-size: 0.9rem;
  color: #555;
  transition: all 0.15s;
}

.logout-btn:hover {
  background: #f8d7da;
  border-color: #dc3545;
  color: #dc3545;
}

.main-content {
  flex: 1;
}

@media (max-width: 600px) {
  .navbar {
    padding: 0 1rem;
    height: auto;
    flex-wrap: wrap;
    gap: 0.5rem;
    padding-top: 0.6rem;
    padding-bottom: 0.6rem;
  }

  .nav-right {
    gap: 0.75rem;
  }

  .nav-link {
    font-size: 0.85rem;
  }
}
</style>
