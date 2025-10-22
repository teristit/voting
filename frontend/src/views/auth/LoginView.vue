<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full space-y-8 p-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Р’С…РѕРґ РІ СЃРёСЃС‚РµРјСѓ
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          РСЃРїРѕР»СЊР·СѓР№С‚Рµ Telegram РґР»СЏ Р°РІС‚РѕСЂРёР·Р°С†РёРё
        </p>
      </div>
      <div class="mt-8 space-y-6">
        <button
          @click="handleTelegramAuth"
          class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          Р’РѕР№С‚Рё С‡РµСЂРµР· Telegram
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const handleTelegramAuth = async () => {
  try {
    await authStore.initAuth()
  } catch (error) {
    console.error('Auth failed:', error)
  }
}
</script>
