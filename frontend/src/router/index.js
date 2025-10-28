import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true, hideHeader: true }
  },
  {
    path: '/voting',
    name: 'Voting',
    component: () => import('@/views/VotingView.vue'),
    meta: { requiresAuth: true }
  },
  // ... остальные маршруты
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Навигационный guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.public && authStore.isAuthenticated) {
    // Перенаправляем авторизованных пользователей с публичных страниц
    next(authStore.isAdmin ? '/admin' : '/voting')
  } else {
    next()
  }
})

export default router