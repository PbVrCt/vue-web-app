<template>
  <div class="container">
    <h3>Estabilidad de Taludes</h3>
    <h1>Registrarse como usuario</h1>
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
            oninput="this.value=this.value.replace(/[^a-zA-Z0-9]/g,'');"
            placeholder="(al menos 5 letras)"
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
            id="password"
            required
            type="password"
            placeholder="(al menos 5 letras)"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errPassword }"
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
      <button @click="guardar" type="button" class="btn btn-primary btn-sm">
        Registrar nuevo usuario
      </button>
      <router-link to="/login" class="btn btn-secondary btn-sm ms-3">Iniciar sesión</router-link>
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
const password2 = ref('') // Repetición Contraseña
const error = ref('') // Error
const intentoValidar = ref(false) // Intento Validar

const errUsername = computed(() => username.value.length < 5)
const errPassword = computed(() => password.value.length < 5)
const errPassword2 = computed(() => password2.value !== password.value)

// UN USUARIO SE REGISTRA
function guardar() {
  if (errUsername.value || errPassword.value || errPassword2.value) {
    intentoValidar.value = true
  } else {
    axios
      .post('/token/register', {
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
