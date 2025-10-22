<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="flex justify-center">
        <div class="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center">
          <span class="text-white text-2xl font-bold">П</span>
        </div>
      </div>
      <h2 class="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">
        Умная премия
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Система голосования и распределения премий
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <!-- Telegram WebApp Auth -->
        <div v-if="isTelegramWebApp" class="space-y-6">
          <div class="text-center">
            <p class="text-sm text-gray-600 mb-4">
              Для входа в систему используется авторизация через Telegram
            </p>
            <button
              @click="handleTelegramAuth"
              :disabled="loading"
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#2481cc] hover:bg-[#1c6ca5] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#2481cc] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <span v-if="loading" class="flex items-center">
                <LoadingSpinner class="w-4 h-4 mr-2" />
                Вход через Telegram...
              </span>
              <span v-else class="flex items-center">
                <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.139c-.197-.125-4.708-2.043-5.169-2.236-.46-.193-1.001-.159-1.345.121-.344.28-.432.766-.217 1.155.215.389 1.548 1.578 2.238 2.236.69.658 2.73 2.236 3.345 2.236.614 0 .921-.28 1.077-.614.156-.334.614-1.578.921-2.236.307-.658.153-1.155-.153-1.312-.307-.156-1.001-.28-1.697-.56z"/>
                </svg>
                Войти через Telegram
              </span>
            </button>
          </div>
        </div>

        <!-- Fallback для обычного браузера -->
        <div v-else class="space-y-6">
          <div class="text-center">
            <p class="text-sm text-gray-600 mb-4">
              Для доступа к системе требуется авторизация через Telegram WebApp
            </p>
            <div class="bg-yellow-50 border border-yellow-200 rounded-md p-4">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="ml-3">
                  <h3 class="text-sm font-medium text-yellow-800">
                    Требуется Telegram
                  </h3>
                  <div class="mt-2 text-sm text-yellow-700">
                    <p>Откройте это приложение в Telegram для авторизации.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Ошибка -->
        <div v-if="error" class="mt-4 bg-red-50 border border-red-200 rounded-md p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">
                Ошибка авторизации
              </h3>
              <div class="mt-2 text-sm text-red-700">
                <p>{{ error }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Демо информация -->
      <div class="mt-6 text-center">
        <p class="text-xs text-gray-500">
          Система предназначена для внутреннего использования сотрудниками компании
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

export default {
  name: 'LoginView',
  components: {
    LoadingSpinner
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const loading = ref(false)
    const error = ref(null)

    const isTelegramWebApp = computed(() => {
      return window.Telegram && window.Telegram.WebApp
    })

    const handleTelegramAuth = async () => {
      loading.value = true
      error.value = null

      try {
        await authStore.initAuth()
        
        // Перенаправляем в зависимости от роли
        if (authStore.isAdmin) {
          await router.push('/admin')
        } else {
          await router.push('/voting')
        }
      } catch (err) {
        error.value = err.message || 'Произошла ошибка при авторизации'
        console.error('Login error:', err)
      } finally {
        loading.value = false
      }
    }

    // Проверяем, может пользователь уже авторизован
    onMounted(async () => {
      authStore.restoreSession()
      
      if (authStore.isAuthenticated) {
        if (authStore.isAdmin) {
          await router.push('/admin')
        } else {
          await router.push('/voting')
        }
      }
    })

    return {
      loading,
      error,
      isTelegramWebApp,
      handleTelegramAuth
    }
  }
}
</script>