<template>
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Логотип и название -->
          <div class="flex items-center">
            <router-link to="/" class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span class="text-white font-bold text-sm">П</span>
              </div>
              <span class="text-xl font-semibold text-gray-900">Умная премия</span>
            </router-link>
          </div>
  
          <!-- Навигация -->
          <div class="flex items-center space-x-4">
            <router-link to="/voting" class="text-gray-600 hover:text-gray-900">Голосование</router-link>
            <router-link to="/results" class="text-gray-600 hover:text-gray-900">Результаты</router-link>
          </div>
  
          <!-- Правая часть -->
          <div class="flex items-center space-x-4">
            <button class="text-gray-400 hover:text-gray-500">Выйти</button>
          </div>
        </div>
      </div>
    </header>
  </template>
  
  <script>
  export default {
    name: 'AppHeader'
  }
  </script>