<template>
  <div class="container">
    <h1>Cambiar contraseña propia</h1>
    <h3 class="text-danger">{{ error }}</h3>
    <form>
      <div class="row mb-3">
        <div class="col-md-4">
          Usuario:
          <span class="h6">{{ username }}</span>
        </div>
      </div>
      <div class="row mb-3">
        <div class="col-md-4">
          <label for="oldPassword" class="form-label">Contraseña actual</label>
          <input
            v-model="oldPassword"
            id="oldPassword"
            required
            type="password"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errOldPassword }"
          />
          <div class="invalid-feedback">Se necesita una contraseña válida</div>
        </div>
      </div>
      <div class="row mb-3">
        <div class="col-md-4">
          <label for="newPassword" class="form-label">Contraseña nueva</label>
          <input
            v-model="newPassword"
            id="newPassword"
            required
            type="password"
            placeholder="(al menos 5 letras)"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errNewPassword }"
          />
          <div class="invalid-feedback">Se necesita una contraseña con al menos 5 letras</div>
        </div>
      </div>
      <div class="row mb-3">
        <div class="col-md-4">
          <label for="password2" class="form-label">Repetir contraseña</label>
          <input
            v-model="password2"
            @keyup.enter="guardar"
            id="password2"
            required
            type="password"
            placeholder="(repetir contraseña)"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errPassword2 }"
          />
          <div class="invalid-feedback">La contraseña debe repetirse correctamente</div>
        </div>
      </div>
    </form>
    <div class="mt-3">
      <router-link to="/" class="btn btn-secondary btn-sm">Atrás</router-link>
      <button @click="guardar" type="button" class="btn btn-primary btn-sm ms-3">
        Cambiar contraseña
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { getCookie } from '../functions/Cookie'
import type { Auth } from '../types/auth'

const router = useRouter()

const username = ref('') // Usuario
const oldPassword = ref('') // Contraseña actual
const newPassword = ref('') // Contraseña nueva
const password2 = ref('') // Repetición Contraseña
const error = ref('') // Error
const intentoValidar = ref(false) // Intento Validar

const errOldPassword = computed(() => oldPassword.value.length < 5)
const errNewPassword = computed(() => newPassword.value.length < 5)
const errPassword2 = computed(() => password2.value !== newPassword.value)

// EL USUARIO MODIFICA SU PROPIA CONTRASEÑA
function guardar() {
  if (errOldPassword.value || errNewPassword.value || errPassword2.value) {
    intentoValidar.value = true
  } else {
    axios
      .put(
        '/api/pwduser',
        {
          oldPassword: oldPassword.value,
          newPassword: newPassword.value
        },
        {
          headers: { 'X-CSRF-TOKEN': getCookie('csrf_access_token') }
        }
      )
      .then(function () {
        axios.post('/token/logout').then(function () {
          router.push('/')
        })
      })
      .catch(function (errorAPI) {
        error.value = errorAPI.response.data.message
      })
  }
}

// REDIRIGIR A LOGIN SI NO ESTA AUTORIZADO; OBTENER USERNAME
function getUsername() {
  axios.get('/api/auth').then(function (response: { data: Auth }) {
    if (!response.data.auth) {
      router.push('/login')
    } else {
      username.value = response.data.username
    }
  })
}

// SE EJECUTA AL MONTAR LA VISTA
onMounted(getUsername)
</script>
