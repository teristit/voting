<template>
    <div>
      <!-- Заголовок и процент -->
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium text-gray-700">Прогресс голосования</span>
        <span class="text-sm font-medium text-primary-600">{{ progress }}%</span>
      </div>
  
      <!-- Прогресс-бар -->
      <div class="w-full bg-gray-200 rounded-full h-2.5">
        <div 
          class="h-2.5 rounded-full transition-all duration-500 ease-out"
          :class="progressBarClass"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>
  
      <!-- Дополнительная информация -->
      <div class="mt-2 flex justify-between text-xs text-gray-500">
        <span>Заполнено</span>
        <span>{{ progress }}/100%</span>
      </div>
  
      <!-- Сообщение о завершении -->
      <div v-if="isComplete" class="mt-3 bg-green-50 border border-green-200 rounded-lg p-3">
        <div class="flex items-center">
          <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span class="text-sm text-green-700 font-medium">Все оценки заполнены! Можете отправлять голоса.</span>
        </div>
      </div>
  
      <!-- Предупреждение о неполном заполнении -->
      <div v-else-if="progress > 0 && progress < 100" class="mt-3 bg-blue-50 border border-blue-200 rounded-lg p-3">
        <div class="flex items-center">
          <svg class="w-4 h-4 text-blue-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-sm text-blue-700">Заполните все оценки для отправки голосов.</span>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { computed } from 'vue'
  
  export default {
    name: 'VotingProgress',
    props: {
      progress: {
        type: Number,
        required: true,
        validator: (value) => value >= 0 && value <= 100
      }
    },
    setup(props) {
      const isComplete = computed(() => props.progress === 100)
  
      const progressBarClass = computed(() => {
        if (props.progress < 30) return 'bg-red-500'
        if (props.progress < 70) return 'bg-yellow-500'
        if (props.progress < 100) return 'bg-blue-500'
        return 'bg-green-500'
      })
  
      return {
        isComplete,
        progressBarClass
      }
    }
  }
  </script>