<template>
  <div class="container">
    <h3>Estabilidad de Taludes</h3>
    <h1>Iniciar sesión</h1>
    <h3 class="text-danger">{{ error }}</h3>
    <form>
      <div class="row mb-3">
        <div class="col-md-4">
          <label for="username" class="form-label">Usuario</label>
          <input
            v-model="username"
            id="username"
            required
            type="text"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errUsername }"
          />
          <div class="invalid-feedback">Se necesita un usuario con al menos 5 letras</div>
        </div>
      </div>
      <div class="row mb-3">
        <div class="col-md-4">
          <label for="password" class="form-label">Contraseña</label>
          <input
            v-model="password"
            @keyup.enter="guardar"
            id="password"
            required
            type="password"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errPassword }"
          />
          <div class="invalid-feedback">Se necesita una contraseña válida</div>
        </div>
      </div>
    </form>
    <div class="mt-3">
      <button @click="guardar" type="button" class="btn btn-primary btn-sm">Iniciar sesión</button>
      <router-link to="/register" class="btn btn-secondary btn-sm ms-3"
        >Registrar nuevo usuario</router-link
      >
    </div>
    <presenta />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import Presenta from '../components/Presenta.vue'

const router = useRouter()

const username = ref('') // Usuario
const password = ref('') // Contraseña
const error = ref('') // Error
const intentoValidar = ref(false) // Intento Validar

const errUsername = computed(() => username.value.length < 5)
const errPassword = computed(() => password.value.length < 5)

// INICIA SESION
function guardar() {
  if (errUsername.value || errPassword.value) {
    intentoValidar.value = true
  } else {
    axios
      .post('/token/login', {
        username: username.value,
        password: password.value
      })
      .then(function () {
        router.push('/')
      })
      .catch(function (errorAPI) {
        error.value = errorAPI.response.data.message
      })
  }
}
</script>
