<template>
  <div class="container">
    <h1>Exportar Talud</h1>
    <h3 class="text-danger">{{ error }}</h3>
    <form>
      <h6>Talud a exportar</h6>
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
      <button @click="exporta" type="button" class="btn btn-primary btn-sm ms-3">
        Exportar Talud
      </button>
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
const idTalud = ref('') // Id Talud Sleccionado
const error = ref('') // Error
const intentoValidar = ref(false) // Intento Validar

const errTalud = computed(() => idTalud.value.length === 0)

// EXPORTA EL TALUD
function exporta() {
  if (errTalud.value) {
    intentoValidar.value = true
  } else {
    axios
      .get('/api/exporta/' + idTalud.value, {
        headers: { 'X-CSRF-TOKEN': getCookie('csrf_access_token') },
        responseType: 'blob'
      })
      .then(function (response) {
        // Obtener el nombre del fichero
        const headerLine = response.headers['content-disposition']
        const startFileNameIndex = headerLine.indexOf('"') + 1
        const endFileNameIndex = headerLine.lastIndexOf('"')
        const filename = headerLine.substring(startFileNameIndex, endFileNameIndex)
        // Descargar el fichero
        const fileURL = window.URL.createObjectURL(new Blob([response.data]))
        const fileLink = document.createElement('a')
        fileLink.href = fileURL
        fileLink.setAttribute('download', filename)
        document.body.appendChild(fileLink)
        fileLink.click()
        // Cambiar a la página de inicio
        router.push('/')
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
