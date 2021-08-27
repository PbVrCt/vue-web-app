<template>
  <div class="container">
    <h1>Cambiar contraseña de usuario</h1>
    <h3 class="text-danger">{{ error }}</h3>
    <form>
      <div class="row mb-3">
        <div class="col-md-4">
          Usuario:
          <span class="h6">{{ user }}</span>
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
      <router-link to="/usuarios" class="btn btn-secondary btn-sm">Atrás</router-link>
      <button @click="guardar" type="button" class="btn btn-primary btn-sm ms-3">
        Cambiar contraseña
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineProps } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { getCookie } from '../functions/Cookie'

const props = defineProps({
  user: String
})

const router = useRouter()

const newPassword = ref('') // Contraseña nueva
const password2 = ref('') // Repetición Contraseña
const error = ref('') // Error
const intentoValidar = ref(false) // Intento Validar

const errNewPassword = computed(() => newPassword.value.length < 5)
const errPassword2 = computed(() => password2.value !== newPassword.value)

// EL ADMINISTRADOR MODIFICA LA CONTRASEÑA DE UN USUARIO
function guardar() {
  if (errNewPassword.value || errPassword2.value) {
    intentoValidar.value = true
  } else {
    axios
      .put(
        '/api/pwdadmin',
        {
          username: props.user,
          newPassword: newPassword.value
        },
        {
          headers: { 'X-CSRF-TOKEN': getCookie('csrf_access_token') }
        }
      )
      .then(function () {
        router.push('/usuarios')
      })
      .catch(function (errorAPI) {
        error.value = errorAPI.response.data.message
      })
  }
}
</script>
