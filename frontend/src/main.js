import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import Toast from './plugins/toast'
import i18n from './i18n'

createApp(App)
  .use(store)
  .use(router)
  .use(Toast)
  .use(i18n)
  .mount('#app')