import axios from 'axios'
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Pwduser from '../views/Pwduser.vue'
import Usuarios from '../views/Usuarios.vue'
import Pwdadmin from '../views/Pwdadmin.vue'
import Userborra from '../views/Userborra.vue'
import Nuevo from '../views/Nuevo.vue'
import Copia from '../views/Copia.vue'
import Exporta from '../views/Exporta.vue'
import Importa from '../views/Importa.vue'
import Borra from '../views/Borra.vue'
import Paso1 from '../views/Paso1.vue'
import Paso2 from '../views/Paso2.vue'
import Paso3 from '../views/Paso3.vue'
import Paso4 from '../views/Paso4.vue'
import Paso5 from '../views/Paso5.vue'
import Paso6 from '../views/Paso6.vue'
import Paso7 from '../views/Paso7.vue'
import Paso8 from '../views/Paso8.vue'
import Paso9 from '../views/Paso9.vue'
import Paso10 from '../views/Paso10.vue'
import Paso11 from '../views/Paso11.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/pwduser',
    name: 'Pwduser',
    component: Pwduser
  },
  {
    path: '/usuarios',
    name: 'Usuarios',
    component: Usuarios
  },
  {
    path: '/pwdadmin/:user/',
    name: 'Pwdadmin',
    component: Pwdadmin,
    props: true
  },
  {
    path: '/userborra/:user/',
    name: 'Userborra',
    component: Userborra,
    props: true
  },
  {
    path: '/nuevo',
    name: 'Nuevo',
    component: Nuevo
  },
  {
    path: '/copia',
    name: 'Copia',
    component: Copia
  },
  {
    path: '/exporta',
    name: 'Exporta',
    component: Exporta
  },
  {
    path: '/importa',
    name: 'Importa',
    component: Importa
  },
  {
    path: '/borra',
    name: 'Borra',
    component: Borra
  },
  {
    path: '/paso1/:idTalud',
    name: 'Paso1',
    component: Paso1,
    props: (route) => {
      const id = Number.parseInt(route.params.idTalud as string)
      return { idTalud: Number.isNaN(id) ? 0 : id }
    }
  },
  {
    path: '/paso2/:idTalud',
    name: 'Paso2',
    component: Paso2,
    props: (route) => {
      const id = Number.parseInt(route.params.idTalud as string)
      return { idTalud: Number.isNaN(id) ? 0 : id }
    }
  },
  {
    path: '/paso3/:idTalud',
    name: 'Paso3',
    component: Paso3,
    props: (route) => {
      const id = Number.parseInt(route.params.idTalud as string)
      return { idTalud: Number.isNaN(id) ? 0 : id }
    }
  },
  {
    path: '/paso4/:idTalud',
    name: 'Paso4',
    component: Paso4,
    props: (route) => {
      const id = Number.parseInt(route.params.idTalud as string)
      return { idTalud: Number.isNaN(id) ? 0 : id }
    }
  },
  {
    path: '/paso5/:idTalud',
    name: 'Paso5',
    component: Paso5,
    props: (route) => {
      const id = Number.parseInt(route.params.idTalud as string)
      return { idTalud: Number.isNaN(id) ? 0 : id }
    }
  },
  {
    path: '/paso6/:idTalud',
    name: 'Paso6',
    component: Paso6,
    props: (route) => {
      const id = Number.parseInt(route.params.idTalud as string)
      return { idTalud: Number.isNaN(id) ? 0 : id }
    }
  },
  {
    path: '/paso7/:idTalud',
    name: 'Paso7',
    component: Paso7,
    props: (route) => {
      const id = Number.parseInt(route.params.idTalud as string)
      return { idTalud: Number.isNaN(id) ? 0 : id }
    }
  },
  {
    path: '/paso8/:idTalud',
    name: 'Paso8',
    component: Paso8,
    props: (route) => {
      const id = Number.parseInt(route.params.idTalud as string)
      return { idTalud: Number.isNaN(id) ? 0 : id }
    }
  },
  {
    path: '/paso9/:idTalud',
    name: 'Paso9',
    component: Paso9,
    props: (route) => {
      const id = Number.parseInt(route.params.idTalud as string)
      return { idTalud: Number.isNaN(id) ? 0 : id }
    }
  },
  {
    path: '/paso10/:idTalud',
    name: 'Paso10',
    component: Paso10,
    props: (route) => {
      const id = Number.parseInt(route.params.idTalud as string)
      return { idTalud: Number.isNaN(id) ? 0 : id }
    }
  },
  {
    path: '/paso11/:idTalud',
    name: 'Paso11',
    component: Paso11,
    props: (route) => {
      const id = Number.parseInt(route.params.idTalud as string)
      return { idTalud: Number.isNaN(id) ? 0 : id }
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

axios.interceptors.response.use(
  function (response) {
    return response
  },
  function (error) {
    console.log(error.response.data)
    if (error.response.status === 401) {
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default router
