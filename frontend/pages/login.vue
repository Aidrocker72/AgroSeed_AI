<template>
 <div class="login-container">
    <div class="login-form">
      <h2>Вход в систему</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Email:</label>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            required 
            placeholder="Введите ваш email"
          />
        </div>
        <div class="form-group">
          <label for="password">Пароль:</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            required 
            placeholder="Введите ваш пароль"
          />
        </div>
        <button type="submit" :disabled="loading" class="login-btn">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
      </form>
      <p class="register-link">
        Нет аккаунта? <NuxtLink to="/register">Зарегистрироваться</NuxtLink>
      </p>
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'auth'
})

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const authStore = useAuthStore()
const router = useRouter()

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    await authStore.login(email.value, password.value)
    await router.push('/dashboard')
  } catch (err: any) {
    error.value = err.data?.detail || err.message || 'Ошибка входа'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.login-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 0.5rem;
 border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.login-btn {
  width: 100%;
  padding: 0.75rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.login-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.register-link {
  margin-top: 1rem;
  text-align: center;
}

.error-message {
  margin-top: 1rem;
  padding: 0.5rem;
 background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  text-align: center;
}
</style>