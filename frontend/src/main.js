import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { init } from '@twa-dev/sdk'

import App from './App.vue'
import './style.css'

// Инициализация Telegram WebApp
init()

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)

app.mount('#app')