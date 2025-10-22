<template>
  <nav class="hidden md:flex space-x-8">
    <!-- Основная навигация для всех пользователей -->
    <router-link
      to="/voting"
      class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors"
      :class="[
        $route.path === '/voting' 
          ? 'border-primary-500 text-gray-900' 
          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
      ]"
    >
      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      Голосование
    </router-link>

    <router-link
      to="/results"
      class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors"
      :class="[
        $route.path === '/results' 
          ? 'border-primary-500 text-gray-900' 
          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
      ]"
    >
      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      Результаты
    </router-link>

    <!-- Админская навигация -->
    <router-link
      v-if="isAdmin"
      to="/admin"
      class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors"
      :class="[
        $route.path.startsWith('/admin') 
          ? 'border-primary-500 text-gray-900' 
          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
      ]"
    >
      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
      Админ-панель
    </router-link>
  </nav>
</template>

<script>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Navigation',
  setup() {
    const authStore = useAuthStore()

    const isAdmin = computed(() => authStore.isAdmin)

    return {
      isAdmin
    }
  }
}
</script>
