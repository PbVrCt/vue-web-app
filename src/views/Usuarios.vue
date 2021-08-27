<template>
  <div class="container">
    <h1>Usuarios</h1>
    <table class="table">
      <thead>
        <tr>
          <th scope="col">Usuario</th>
          <th scope="col">F. Registro</th>
          <th scope="col">F. Último Acceso</th>
          <th scope="col"></th>
          <th scope="col"></th>
        </tr>
      </thead>
      <tbody v-for="usuario in usuarios" :key="usuario.username">
        <tr>
          <th scope="row">{{ usuario.username }}</th>
          <td>{{ usuario.createDate }}</td>
          <td>{{ usuario.accessDate }}</td>
          <td>
            <router-link
              v-if="!usuario.admin"
              :to="{ path: '/pwdadmin/' + usuario.username + '/' }"
              class="btn btn-outline-secondary btn-sm"
              >Cambiar Contraseña</router-link
            >
          </td>
          <td>
            <router-link
              v-if="!usuario.admin"
              :to="{ path: '/userborra/' + usuario.username + '/' }"
              class="btn btn-danger btn-sm"
              >Eliminar Usuario</router-link
            >
          </td>
        </tr>
      </tbody>
    </table>
    <div class="mt-3">
      <router-link to="/" class="btn btn-secondary btn-sm">Atrás</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import type { Usuario } from '../types/usuario'

const usuarios = ref<Usuario[]>([]) // Usuarios

// OBTENER LOS USUARIOS
function getUsuarios() {
  axios.get('/api/usuarios').then(function (response: { data: Usuario[] }) {
    usuarios.value = response.data
  })
}

// SE EJECUTA AL MONTAR LA VISTA
onMounted(getUsuarios)
</script>
