<template>
  <div class="register-container">
    <div class="register-form">
      <h2>Регистрация</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="name">Имя:</label>
          <input 
            type="text" 
            id="name" 
            v-model="name" 
            placeholder="Введите ваше имя"
          />
        </div>
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
        <div class="form-group">
          <label for="confirmPassword">Подтвердите пароль:</label>
          <input 
            type="password" 
            id="confirmPassword" 
            v-model="confirmPassword" 
            required 
            placeholder="Подтвердите ваш пароль"
          />
        </div>
        <button type="submit" :disabled="loading" class="register-btn">
          {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </button>
      </form>
      <p class="login-link">
        Уже есть аккаунт? <NuxtLink to="/login">Войти</NuxtLink>
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

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')

const authStore = useAuthStore()
const router = useRouter()

const handleRegister = async () => {
  if (password.value !== confirmPassword.value) {
    error.value = 'Пароли не совпадают'
    return
  }
  
  loading.value = true
 error.value = ''
  
  try {
    await authStore.register(email.value, password.value, name.value)
    await router.push('/login')
  } catch (err: any) {
    error.value = err.message || 'Ошибка регистрации'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.register-form {
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

.register-btn {
  width: 100%;
  padding: 0.75rem;
  background-color: #28a745;
  color: white;
 border: none;
 border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.register-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.login-link {
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