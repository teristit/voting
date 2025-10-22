<template>
  <slot v-if="isAuthenticated && hasRequiredRole" />
  <div v-else-if="loading" class="flex justify-center items-center min-h-screen">
    <LoadingSpinner size="lg" />
  </div>
  <UnauthorizedView v-else />
</template>

<script>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import UnauthorizedView from '@/views/errors/UnauthorizedView.vue'

export default {
  name: 'AuthGuard',
  components: {
    LoadingSpinner,
    UnauthorizedView
  },
  props: {
    requiredRole: {
      type: String,
      default: null,
      validator: (value) => [null, 'user', 'manager', 'admin'].includes(value)
    }
  },
  setup(props) {
    const router = useRouter()
    const authStore = useAuthStore()

    const isAuthenticated = computed(() => authStore.isAuthenticated)
    const loading = computed(() => authStore.loading)

    const hasRequiredRole = computed(() => {
      if (!props.requiredRole) return true
      
      const userRole = authStore.user?.role
      const roleHierarchy = { user: 1, manager: 2, admin: 3 }
      
      return roleHierarchy[userRole] >= roleHierarchy[props.requiredRole]
    })

    // Проверяем авторизацию при монтировании
    onMounted(async () => {
      if (!authStore.isAuthenticated) {
        authStore.restoreSession()
        
        if (!authStore.isAuthenticated) {
          // Пытаемся авторизоваться через Telegram, если есть данные
          if (window.Telegram?.WebApp?.initData) {
            try {
              await authStore.initAuth()
            } catch (error) {
              console.error('Auto-auth failed:', error)
              router.push('/login')
            }
          } else {
            router.push('/login')
          }
        }
      }
    })

    return {
      isAuthenticated,
      loading,
      hasRequiredRole
    }
  }
}
</script>
