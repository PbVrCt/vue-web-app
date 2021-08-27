<template>
  <div class="container">
    <h1>Crear Talud</h1>
    <h3 class="text-danger">{{ error }}</h3>
    <!-- Cuando un Form tiene un solo Input con @keyup.enter es necesario @submit.prevent -->
    <form @submit.prevent>
      <div class="row mb-3">
        <div class="col-md-9">
          <label for="nombre" class="form-label">Nombre del talud</label>
          <input
            v-model="nombre"
            @keyup.enter="guardar"
            id="nombre"
            required
            type="text"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errNombre }"
          />
          <div class="invalid-feedback">Es necesario un nombre</div>
        </div>
      </div>
    </form>
    <div class="mt-3">
      <router-link to="/" class="btn btn-secondary btn-sm">Atrás</router-link>
      <button @click="guardar" type="button" class="btn btn-primary btn-sm ms-3">
        Crear Talud
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { getCookie } from '../functions/Cookie'

const router = useRouter()

const nombre = ref('') // Nombre
const error = ref('') // Error
const intentoValidar = ref(false) // Intento Validar

const errNombre = computed(() => nombre.value.length === 0)

// CREA NUEVO TALUD
function guardar() {
  if (errNombre.value) {
    intentoValidar.value = true
  } else {
    axios
      .post(
        '/api/nuevo',
        {
          nombre: nombre.value
        },
        {
          headers: { 'X-CSRF-TOKEN': getCookie('csrf_access_token') }
        }
      )
      .then(function (response) {
        if (response.data.codigo === 0) {
          error.value = 'El nombre del talud ya existe'
        } else {
          router.push('/paso1/' + response.data.codigo)
        }
      })
      .catch(function (errorAPI) {
        error.value = errorAPI.response.data.message
      })
  }
}
</script>
