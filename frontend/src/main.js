import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'

// Инициализируем Telegram WebApp
if (window.Telegram && window.Telegram.WebApp) {
  window.Telegram.WebApp.ready()
  window.Telegram.WebApp.expand()
  
  // Настраиваем тему
  if (window.Telegram.WebApp.themeParams) {
    document.documentElement.style.setProperty('--tg-theme-bg-color', window.Telegram.WebApp.themeParams.bg_color || '#ffffff')
    document.documentElement.style.setProperty('--tg-theme-text-color', window.Telegram.WebApp.themeParams.text_color || '#000000')
    document.documentElement.style.setProperty('--tg-theme-hint-color', window.Telegram.WebApp.themeParams.hint_color || '#999999')
    document.documentElement.style.setProperty('--tg-theme-link-color', window.Telegram.WebApp.themeParams.link_color || '#2481cc')
    document.documentElement.style.setProperty('--tg-theme-button-color', window.Telegram.WebApp.themeParams.button_color || '#2481cc')
    document.documentElement.style.setProperty('--tg-theme-button-text-color', window.Telegram.WebApp.themeParams.button_text_color || '#ffffff')
  }
}

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Глобальные свойства
app.config.globalProperties.$tg = window.Telegram?.WebApp || {}

app.mount('#app')
