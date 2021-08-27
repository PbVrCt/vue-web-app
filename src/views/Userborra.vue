<template>
  <div class="container">
    <h1>Eliminar usuario</h1>
    <h3 class="text-danger">{{ error }}</h3>
    <form>
      <div class="row mb-3">
        <div class="col-md-4">
          Usuario:
          <span class="h6">{{ user }}</span>
        </div>
      </div>
    </form>
    <div class="mt-3">
      <router-link to="/usuarios" class="btn btn-secondary btn-sm">Atrás</router-link>
      <button @click="borrar" type="button" class="btn btn-danger btn-sm ms-3">
        Eliminar usuario
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { getCookie } from '../functions/Cookie'

const props = defineProps({
  user: String
})

const router = useRouter()

const error = ref('') // Error

// EL ADMINISTRADOR ELIMINA UN USUARIO
function borrar() {
  axios
    .delete('/api/deleteuser/' + props.user, {
      headers: { 'X-CSRF-TOKEN': getCookie('csrf_access_token') }
    })
    .then(function () {
      router.push('/usuarios')
    })
    .catch(function (errorAPI) {
      error.value = errorAPI.response.data.message
    })
}
</script>
