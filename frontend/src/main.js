import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import './style.css'

// Временно закомментируем Telegram SDK для тестирования
// import { init } from '@twa-dev/sdk'
// init()

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)

app.mount('#app')