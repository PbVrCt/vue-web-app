import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import 'vue-universal-modal/dist/index.css'
import VueUniversalModal from 'vue-universal-modal'

const app = createApp(App)
  .use(VueUniversalModal, { teleportTarget: '#modals' })
  .use(router)
  .mount('#app')
