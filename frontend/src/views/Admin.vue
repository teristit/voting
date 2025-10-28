<template>
  <div class="space-y-6">
    <!-- Заголовок -->
    <div class="text-center">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Администрирование</h1>
      <p class="text-gray-600">Управление системой голосования</p>
    </div>

    <!-- Проверка прав -->
    <div v-if="!authStore.isAdmin" class="card text-center">
      <div class="text-red-500 mb-4">
        <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
        </svg>
      </div>
      <h3 class="text-xl font-semibold mb-3">Доступ запрещен</h3>
      <p class="text-hint">У вас недостаточно прав для доступа к панели администрирования</p>
    </div>

    <!-- Панель администратора -->
    <div v-else>
      <!-- Быстрые действия -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="card text-center hover:shadow-md transition-shadow cursor-pointer" @click="manageCurrentSession">
          <div class="text-blue-500 mb-3">
            <svg class="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <h3 class="font-semibold mb-1">Управление сессией</h3>
          <p class="text-sm text-hint">Создание, редактирование, закрытие сессий</p>
        </div>
        
        <div class="card text-center hover:shadow-md transition-shadow cursor-pointer" @click="manageParticipants">
          <div class="text-green-500 mb-3">
            <svg class="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>
          </div>
          <h3 class="font-semibold mb-1">Участники</h3>
          <p class="text-sm text-hint">Управление списком участников</p>
        </div>
        
        <div class="card text-center hover:shadow-md transition-shadow cursor-pointer" @click="viewReports">
          <div class="text-purple-500 mb-3">
            <svg class="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <h3 class="font-semibold mb-1">Отчеты</h3>
          <p class="text-sm text-hint">Экспорт данных и аналитика</p>
        </div>
        
        <div class="card text-center hover:shadow-md transition-shadow cursor-pointer" @click="systemSettings">
          <div class="text-orange-500 mb-3">
            <svg class="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
          </div>
          <h3 class="font-semibold mb-1">Настройки</h3>
          <p class="text-sm text-hint">Системные параметры</p>
        </div>
      </div>

      <!-- Текущая статистика -->
      <div class="card">
        <h3 class="text-lg font-semibold mb-4">Текущая статистика</h3>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="text-center p-4 bg-blue-50 rounded-lg">
            <div class="text-2xl font-bold text-blue-600">{{ stats.totalUsers || 0 }}</div>
            <div class="text-sm text-blue-600">всего пользователей</div>
          </div>
          <div class="text-center p-4 bg-green-50 rounded-lg">
            <div class="text-2xl font-bold text-green-600">{{ stats.activeUsers || 0 }}</div>
            <div class="text-sm text-green-600">активных пользователей</div>
          </div>
          <div class="text-center p-4 bg-purple-50 rounded-lg">
            <div class="text-2xl font-bold text-purple-600">{{ stats.totalSessions || 0 }}</div>
            <div class="text-sm text-purple-600">всего сессий</div>
          </div>
          <div class="text-center p-4 bg-orange-50 rounded-lg">
            <div class="text-2xl font-bold text-orange-600">{{ stats.totalVotes || 0 }}</div>
            <div class="text-sm text-orange-600">всего голосов</div>
          </div>
        </div>
      </div>

      <!-- Заглушка для полного функционала -->
      <div class="card">
        <h3 class="text-lg font-semibold mb-4">Администрирование (в разработке)</h3>
        <div class="bg-blue-50 p-4 rounded-lg">
          <p class="text-blue-900 mb-3">Полный функционал администрирования включает:</p>
          <ul class="text-sm text-blue-700 space-y-1">
            <li>• Создание и управление сессиями голосования</li>
            <li>• Массовое добавление участников через CSV</li>
            <li>• Настройка параметров бонусов</li>
            <li>• Мониторинг процесса голосования в реальном времени</li>
            <li>• Экспорт результатов для бухгалтерии</li>
            <li>• Логирование действий пользователей</li>
            <li>• Системные настройки и резервное копирование</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Состояние
const stats = ref({
  totalUsers: 0,
  activeUsers: 0,
  totalSessions: 0,
  totalVotes: 0
})

// Методы (заглушки)
const manageCurrentSession = () => {
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.showAlert('Управление сессиями будет доступно в полной версии администрирования')
  }
}

const manageParticipants = () => {
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.showAlert('Управление участниками будет доступно в полной версии администрирования')
  }
}

const viewReports = () => {
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.showAlert('Отчеты и экспорт данных будут доступны в полной версии администрирования')
  }
}

const systemSettings = () => {
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.showAlert('Системные настройки будут доступны в полной версии администрирования')
  }
}

const loadStats = async () => {
  // Заглушка для загрузки статистики
  // В реальной версии здесь будет вызов API
  stats.value = {
    totalUsers: 42,
    activeUsers: 38,
    totalSessions: 15,
    totalVotes: 485
  }
}

// Жизненный цикл
onMounted(() => {
  if (!authStore.isAdmin) {
    return
  }
  loadStats()
})
</script>