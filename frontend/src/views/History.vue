<template>
  <div class="space-y-6">
    <!-- Заголовок -->
    <div class="text-center">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">История сессий</h1>
      <p class="text-gray-600">Просмотр результатов прошлых сессий голосования</p>
    </div>

    <!-- Заглушка -->
    <div class="card text-center">
      <div class="text-blue-500 mb-4">
        <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
      </div>
      <h3 class="text-xl font-semibold mb-3">История сессий</h3>
      <p class="text-hint mb-6 max-w-md mx-auto">
        Здесь будет отображаться история всех сессий голосования с возможностью просмотра детальных результатов
      </p>
      <div class="bg-blue-50 p-4 rounded-lg">
        <h4 class="font-semibold text-blue-900 mb-2">Функции в разработке:</h4>
        <ul class="text-sm text-blue-700 space-y-1">
          <li>• Список всех завершенных сессий</li>
          <li>• Детальные результаты каждой сессии</li>
          <li>• Статистика личных результатов</li>
          <li>• Фильтрация по датам и периодам</li>
          <li>• Экспорт данных</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
// Пока это заглушка для истории сессий
// В будущем здесь будет полноценный функционал
</script>