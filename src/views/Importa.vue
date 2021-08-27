<template>
  <div class="container">
    <h1>Importar Talud</h1>
    <h3 class="text-danger">{{ error }}</h3>
    <form>
      <div class="row mb-3">
        <div class="col-md-9">
          <label for="file" class="form-label">Fichero del talud</label>
          <input
            ref="fileInput"
            id="file"
            name="file"
            required
            type="file"
            value=""
            class="form-control"
            accept="application/JSON"
            :class="{ 'is-invalid': intentoValidar && errFichero }"
          />
          <div class="invalid-feedback">Es necesario seleccionar un fichero</div>
        </div>
      </div>
    </form>
    <div class="mt-3">
      <router-link to="/" class="btn btn-secondary btn-sm">Atrás</router-link>
      <button @click="importa" type="button" class="btn btn-primary btn-sm ms-3">
        Importar Talud
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

const fileInput = ref<HTMLInputElement | null>(null) // Input Fichero
const error = ref('') // Error
const intentoValidar = ref(false) // Intento Validar

const errFichero = computed(() => fileInput.value?.files?.length === 0)

// IMPORTA EL TALUD
function importa() {
  if (errFichero.value) {
    intentoValidar.value = true
  } else {
    const formData = new FormData()
    formData.append('file', fileInput.value?.files?.item(0) as Blob)
    axios
      .post('/api/importa', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-CSRF-TOKEN': getCookie('csrf_access_token')
        }
      })
      .then(function (response) {
        if (response.data.codigo === 0) {
          error.value = 'Error al importar el talud desde el fichero'
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
