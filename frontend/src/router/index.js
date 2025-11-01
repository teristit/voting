import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// Ленивая загрузка компонентов
const Home = () => import('../views/Home.vue')
const Voting = () => import('../views/Voting.vue')
const Results = () => import('../views/Results.vue')
const History = () => import('../views/History.vue')
const Profile = () => import('../views/Profile.vue')
const Admin = () => import('../views/Admin.vue')
const NotFound = () => import('../views/NotFound.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      requiresAuth: true,
      title: 'Главная'
    }
  },
  {
    path: '/voting',
    name: 'Voting',
    component: Voting,
    meta: {
      requiresAuth: true,
      title: 'Голосование'
    }
  },
  {
    path: '/results',
    name: 'Results',
    component: Results,
    meta: {
      requiresAuth: true,
      title: 'Результаты'
    }
  },
  {
    path: '/history',
    name: 'History',
    component: History,
    meta: {
      requiresAuth: true,
      title: 'История'
    }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: {
      requiresAuth: true,
      title: 'Профиль'
    }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: 'Администрирование'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: {
      title: 'Страница не найдена'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Охранники навигации
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Обновляем заголовок страницы
  if (to.meta.title) {
    document.title = `${to.meta.title} - Умная Премия`
  }
  
  // Проверяем аутентификацию
  if (to.meta.requiresAuth) {
    // Если стор еще не инициализирован, ждем
    if (!authStore.initialized) {
      await authStore.init()
    }
    
    // Проверяем, что пользователь аутентифицирован
    if (!authStore.isAuthenticated) {
      // Перенаправляем на главную страницу, где будет отображен экран входа
      return next('/')
    }
    
    // Проверяем права администратора
    if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
      // Показываем уведомление об ошибке через Telegram
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert('Недостаточно прав для доступа к этой странице')
      }
      return next('/')
    }
  }
  
  next()
})

// Ошибки навигации
router.onError((error) => {
  console.error('Ошибка навигации:', error)
  
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.showAlert('Ошибка при загрузке страницы')
  }
})

export default router
