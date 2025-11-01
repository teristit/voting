<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Загрузка -->
    <div v-if="authStore.isLoading" class="loading">
      <div class="spinner"></div>
      <p class="ml-3 text-hint">Загрузка...</p>
    </div>

    <!-- Ошибка аутентификации -->
    <div v-else-if="authStore.error" class="p-4">
      <div class="error-message">
        <h3 class="font-semibold mb-2">Ошибка аутентификации</h3>
        <p>{{ authStore.error }}</p>
        <button @click="authStore.login()" class="btn-primary mt-3">
          Попробовать снова
        </button>
      </div>
    </div>

    <!-- Основное приложение -->
    <div v-else-if="authStore.isAuthenticated" class="flex flex-col min-h-screen">
      <!-- Шапка -->
      <header class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-10">
        <div class="container mx-auto px-4 py-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <span class="text-white font-semibold text-sm">{{getInitials(authStore.user?.name)}}</span>
              </div>
              <div>
                <h1 class="text-lg font-semibold">Умная Премия</h1>
                <p class="text-sm text-hint">Привет, {{ authStore.user?.name }}!</p>
              </div>
            </div>
            
            <div class="flex items-center space-x-2">
              <!-- Нотификации -->
              <div v-if="sessionStore.hasActiveSession" class="flex items-center text-green-600">
                <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                <span class="text-sm">Активная сессия</span>
              </div>
              
              <!-- Меню -->
              <button @click="showMenu = !showMenu" class="p-2 hover:bg-gray-100 rounded-lg relative">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zM12 13a1 1 0 110-2 1 1 0 010 2zM12 20a1 1 0 110-2 1 1 0 010 2z"></path>
                </svg>
                
                <!-- Выпадающее меню -->
                <div v-if="showMenu" class="absolute right-0 top-full mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
                  <router-link to="/profile" @click="showMenu = false" class="block px-4 py-2 text-sm hover:bg-gray-100">
                    Мой профиль
                  </router-link>
                  <router-link v-if="authStore.user?.role === 'admin'" to="/admin" @click="showMenu = false" class="block px-4 py-2 text-sm hover:bg-gray-100">
                    Администрирование
                  </router-link>
                  <hr class="my-1">
                  <button @click="logout" class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100 text-red-600">
                    Выйти
                  </button>
                </div>
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- Навигация -->
      <nav class="bg-white border-b border-gray-200">
        <div class="container mx-auto px-4">
          <div class="flex space-x-6 overflow-x-auto">
            <router-link to="/" class="nav-link">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
              </svg>
              Главная
            </router-link>
            
            <router-link to="/voting" class="nav-link" v-if="sessionStore.hasActiveSession">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              Голосование
            </router-link>
            
            <router-link to="/results" class="nav-link">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              Результаты
            </router-link>
            
            <router-link to="/history" class="nav-link">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              История
            </router-link>
          </div>
        </div>
      </nav>

      <!-- Основной контент -->
      <main class="flex-1 container mx-auto px-4 py-6">
        <Transition name="fade" mode="out-in">
          <router-view :key="$route.fullPath" />
        </Transition>
      </main>
      
      <!-- Подвал -->
      <footer class="bg-white border-t border-gray-200 py-4">
        <div class="container mx-auto px-4 text-center text-sm text-hint">
          <p>Умная Премия v1.0 &copy; 2025</p>
        </div>
      </footer>
    </div>

    <!-- Не аутентифицирован -->
    <div v-else class="flex items-center justify-center min-h-screen p-4">
      <div class="text-center">
        <div class="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
          </svg>
        </div>
        <h2 class="text-xl font-semibold mb-2">Добро пожаловать!</h2>
        <p class="text-hint mb-4">Для продолжения необходимо войти через Telegram</p>
        <button @click="authStore.login()" class="btn-primary">
          Войти через Telegram
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useSessionStore } from './stores/session'

const authStore = useAuthStore()
const sessionStore = useSessionStore()
const showMenu = ref(false)

// Методы
const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(word => word[0]).join('').toUpperCase().substring(0, 2)
}

const logout = async () => {
  showMenu.value = false
  await authStore.logout()
}

// Закрытие меню при клике вне его
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    showMenu.value = false
  }
}

// Жизненный цикл
onMounted(async () => {
  document.addEventListener('click', handleClickOutside)
  
  // Инициализируем аутентификацию
  await authStore.init()
  
  // Если пользователь аутентифицирован, загружаем сессии
  if (authStore.isAuthenticated) {
    await sessionStore.loadCurrentSession()
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.nav-link {
  @apply flex items-center space-x-2 px-4 py-3 text-sm font-medium text-gray-600 hover:text-blue-600 border-b-2 border-transparent hover:border-blue-600 transition-colors whitespace-nowrap;
}

.nav-link.router-link-active {
  @apply text-blue-600 border-blue-600;
}
</style>
