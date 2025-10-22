<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Шапка приложения -->
    <AppHeader v-if="isAuthenticated && showHeader" />

    <!-- Основной контент -->
    <main :class="mainClasses">
      <router-view />
    </main>

    <!-- Глобальные уведомления -->
    <div class="fixed inset-0 flex items-end justify-center px-4 py-6 pointer-events-none sm:p-6 sm:items-start sm:justify-end z-50">
      <Notification
        v-for="notification in notifications"
        :key="notification.id"
        :type="notification.type"
        :title="notification.title"
        :message="notification.message"
        :duration="notification.duration"
        :show="true"
        @close="removeNotification(notification.id)"
      />
    </div>

    <!-- Глобальная загрузка -->
    <div
      v-if="globalLoading"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center"
    >
      <div class="bg-white rounded-lg p-6 shadow-xl">
        <LoadingSpinner size="xl" />
        <p class="mt-4 text-gray-600 text-center">Загрузка...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, provide } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import AppHeader from '@/components/common/AppHeader.vue'
import Notification from '@/components/common/Notification.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

export default {
  name: 'App',
  components: {
    AppHeader,
    Notification,
    LoadingSpinner
  },
  setup() {
    const route = useRoute()
    const authStore = useAuthStore()
    const notificationsStore = useNotificationsStore()

    const isAuthenticated = computed(() => authStore.isAuthenticated)
    const globalLoading = computed(() => authStore.loading)
    const notifications = computed(() => notificationsStore.notifications)

    // Скрываем шапку на странице логина
    const showHeader = computed(() => !route.meta?.hideHeader)

    // Классы для основного контента
    const mainClasses = computed(() => ({
      'min-h-screen': true,
      'pt-16': isAuthenticated.value && showHeader.value // Отступ для фиксированной шапки
    }))

    // Функция для показа уведомлений (предоставляем дочерним компонентам)
    const showNotification = (notification) => {
      notificationsStore.addNotification(notification)
    }

    const removeNotification = (id) => {
      notificationsStore.removeNotification(id)
    }

    // Предоставляем функцию уведомлений дочерним компонентам
    provide('showNotification', showNotification)

    // Восстанавливаем сессию при загрузке приложения
    onMounted(() => {
      authStore.restoreSession()
    })

    return {
      isAuthenticated,
      globalLoading,
      notifications,
      showHeader,
      mainClasses,
      removeNotification
    }
  }
}
</script>