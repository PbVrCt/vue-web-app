<template>
  <div class="container">
    Usuario:
    <span class="h6">{{ usuario }}</span>
    <router-link to="/pwduser" class="btn btn-link text-body text-decoration-none my-3 ms-3"
      >Cambiar contraseña</router-link
    >
    <router-link
      to="/usuarios"
      v-show="isAdmin"
      class="btn btn-link text-body text-decoration-none my-3 ms-3"
      >Usuarios registrados</router-link
    >
    <button @click="logout" type="button" class="btn btn-link text-body text-decoration-none ms-3">
      Cerrar sesión
    </button>
    <h1 class="mt-2">Estabilidad de Taludes</h1>
    <router-link to="/nuevo" class="btn btn-primary btn-sm my-3">Nuevo</router-link>
    <router-link to="/copia" v-show="taludes.length > 0" class="btn btn-secondary btn-sm my-3 ms-2"
      >Copiar</router-link
    >
    <router-link
      to="/exporta"
      v-show="taludes.length > 0"
      class="btn btn-secondary btn-sm my-3 ms-2"
      >Exportar</router-link
    >
    <router-link to="/importa" class="btn btn-secondary btn-sm my-3 ms-2">Importar</router-link>
    <router-link to="/borra" v-show="taludes.length > 0" class="btn btn-danger btn-sm my-3 ms-2"
      >Eliminar</router-link
    >
    <h3 v-show="taludes.length > 0">Taludes</h3>
    <div class="list-group">
      <div v-for="talud in taludes" :key="talud.codigo" class="list-group-item">
        <span class="h4">{{ talud.nombre }}</span>
        <router-link
          v-for="paso in pasos(talud)"
          :key="paso"
          :to="{ path: '/paso' + (paso + 1) + '/' + talud.codigo }"
          class="btn btn-outline-secondary btn-sm ms-2 mb-2"
          >{{ TEXTOSPASOS[paso] }}</router-link
        >
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { usePasos } from '../functions/Pasos'
import type { Auth } from '../types/auth'
import type { TaludBase } from '../types/talud'

const router = useRouter()
const { TEXTOSPASOS, pasos } = usePasos()

const isAdmin = ref(false) // True si el usuario es administrador
const usuario = ref('') // Usuario
const taludes = ref<TaludBase[]>([]) // Taludes

// LOGOUT
function logout() {
  axios.post('/token/logout').then(function () {
    router.push('/login')
  })
}

// OBTENER LOS TALUDES
function getTaludes() {
  axios.get('/api/taludes').then(function (response: { data: TaludBase[] }) {
    taludes.value = response.data
  })
}

// REDIRIGIR A LOGIN SI NO ESTA AUTORIZADO; OBTENER USERNAME
function comprobarAutorizacion() {
  axios.get('/api/auth').then(function (response: { data: Auth }) {
    if (!response.data.auth) {
      router.push('/login')
    } else {
      isAdmin.value = response.data.admin
      usuario.value = response.data.username
      //
      getTaludes()
    }
  })
}

// SE EJECUTA AL MONTAR LA VISTA
onMounted(comprobarAutorizacion)
</script>
