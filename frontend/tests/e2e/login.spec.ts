import { test, expect } from '@playwright/test'

test.describe('Login Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
  })

  test('should render login form', async ({ page }) => {
    await expect(page.locator('h2')).toContainText('Вход в систему')
    await expect(page.locator('#email')).toBeVisible()
    await expect(page.locator('#password')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toContainText('Войти')
  })

  test('should allow user to log in with valid credentials', async ({ page }) => {
    // Заполняем форму валидными данными
    await page.locator('#email').fill('test@example.com')
    await page.locator('#password').fill('password123')
    
    // Отправляем форму
    await page.locator('button[type="submit"]').click()
    
    // Проверяем, что пользователь перенаправлен на главную страницу
    await expect(page).toHaveURL('/dashboard')
  })

  test('should show error with invalid credentials', async ({ page }) => {
    // Заполняем форму невалидными данными
    await page.locator('#email').fill('invalid@example.com')
    await page.locator('#password').fill('wrongpassword')
    
    // Отправляем форму
    await page.locator('button[type="submit"]').click()
    
    // Проверяем, что отображается сообщение об ошибке
    await expect(page.locator('.error-message')).toBeVisible()
  })

  test('should navigate to register page', async ({ page }) => {
    await page.locator('text=Зарегистрироваться').click()
    await expect(page).toHaveURL('/register')
  })
})