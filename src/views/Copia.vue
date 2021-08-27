<template>
  <div class="container">
    <h1>Copiar Talud</h1>
    <h3 class="text-danger">{{ error }}</h3>
    <form>
      <div class="row mb-3">
        <div class="col-md-9">
          <label for="nombre" class="form-label">Nombre del talud</label>
          <input
            v-model="nombre"
            id="nombre"
            required
            type="text"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errNombre }"
          />
          <div class="invalid-feedback">Es necesario un nombre</div>
        </div>
      </div>
      <h6>Talud a copiar</h6>
      <div>
        <template v-for="talud in taludes" :key="talud.codigo">
          <div class="form-check form-check-inline">
            <input
              v-model="idTalud"
              :value="talud.codigo"
              :id="'talud' + talud.codigo"
              name="taludid"
              type="radio"
              class="form-check-input"
            />
            <label :for="'talud' + talud.codigo" class="form-check-label">{{ talud.nombre }}</label>
          </div>
        </template>
        <span :class="{ 'is-invalid': intentoValidar && errTalud }"></span>
        <div class="invalid-feedback">Es necesario seleccionar un talud</div>
      </div>
    </form>
    <div class="mt-3">
      <router-link to="/" class="btn btn-secondary btn-sm">Atrás</router-link>
      <button @click="copia" type="button" class="btn btn-primary btn-sm ms-3">Copiar Talud</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { getCookie } from '../functions/Cookie'
import type { TaludBase } from '../types/talud'

const router = useRouter()

const taludes = ref<TaludBase[]>([]) // Taludes
const nombre = ref('') // Nombre
const idTalud = ref('') // Id Talud Sleccionado
const error = ref('') // Error
const intentoValidar = ref(false) // Intento Validar

const errNombre = computed(() => nombre.value.length === 0)
const errTalud = computed(() => idTalud.value.length === 0)

// COPIA EL TALUD
function copia() {
  if (errNombre.value || errTalud.value) {
    intentoValidar.value = true
  } else {
    axios
      .post(
        '/api/copia',
        {
          nombre: nombre.value,
          idCopiar: idTalud.value
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

// OBTENER LOS TALUDES
function getTaludes() {
  axios.get('/api/taludes').then(function (response: { data: TaludBase[] }) {
    taludes.value = response.data
  })
}

// SE EJECUTA AL MONTAR LA VISTA
onMounted(getTaludes)
</script>
