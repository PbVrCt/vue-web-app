<template>
  <div class="container">
    <h1>{{ talud.nombre + ' - ' + TEXTOSPASOS[NUMPASO - 1] }}</h1>
    <pasos-talud :codigo="talud.codigo" :numpaso="NUMPASO" :pasos="pasos(talud)" />
    <h3 class="text-danger">{{ error }}</h3>
    <form class="row">
      <div class="col-md-8 offset-md-2">
        <div>
          <label for="dovelasX" class="form-label">Número de dovelas en eje X</label>
          <input
            v-model.number="dovelasXtalud"
            id="dovelasX"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errDovelasX }"
            style="width: 200px"
          />
          <div class="invalid-feedback">Es necesario un número entero positivo</div>
        </div>
        <div class="my-3">
          <label for="dovelasAnchoMax" class="form-label">Ancho máximo de dovela (en metros)</label>
          <input
            v-model.number="dovelasAnchoMaxtalud"
            id="dovelasAnchoMax"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errDovelasAnchoMax }"
            style="width: 200px"
          />
          <div class="invalid-feedback">Es necesario un número positivo</div>
        </div>
        <div>
          <template v-for="(tex, num) in metodosTex" :key="num">
            <div class="form-check">
              <input
                v-model="metodoTalud"
                :value="num"
                :id="'met' + num"
                type="radio"
                class="form-check-input"
              />
              <label :for="'met' + num" class="form-check-label">{{ tex }}</label>
            </div>
          </template>
          <span :class="{ 'is-invalid': intentoValidar && errMetodo }"></span>
          <div class="invalid-feedback">Es necesario seleccionar un método</div>
        </div>
      </div>
    </form>
    <div class="my-3">
      <router-link to="/" class="btn btn-secondary btn-sm">Inicio</router-link>
      <router-link
        :to="'/paso' + (NUMPASO - 1) + '/' + talud.codigo"
        class="btn btn-secondary btn-sm ms-3"
        >Anterior</router-link
      >
      <button
        v-if="talud.avance === NUMPASO"
        @click="eliminar"
        type="button"
        class="btn btn-danger btn-sm ms-3"
      >
        Eliminar
      </button>
      <button
        v-if="talud.avance >= NUMPASO"
        @click="deshacer"
        type="button"
        class="btn btn-warning btn-sm ms-3"
      >
        Deshacer
      </button>
      <button @click="guardar" type="button" class="btn btn-primary btn-sm ms-3">Guardar</button>
      <button
        v-if="talud.avance >= NUMPASO"
        @click="analisis"
        type="button"
        class="btn btn-success btn-sm ms-3"
      >
        Guardar y Ejecutar análisis
      </button>
      <router-link
        v-if="talud.avance > NUMPASO"
        :to="'/paso' + (NUMPASO + 1) + '/' + talud.codigo"
        class="btn btn-secondary btn-sm ms-3"
        >Siguiente</router-link
      >
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, defineProps } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { getCookie } from '../functions/Cookie'
import { usePasos } from '../functions/Pasos'
import { taludBase } from '../functions/Base'
import { metodosTex } from '../functions/Metodos'
import type { Talud10 } from '../types/talud'
import PasosTalud from '../components/PasosTalud.vue'

const props = defineProps({
  idTalud: Number
})

const router = useRouter()
const { TEXTOSPASOS, pasos } = usePasos()
const NUMPASO = 10

const talud = reactive({ ...taludBase })
const metodoTalud = ref('')
const dovelasXtalud = ref(10)
const dovelasAnchoMaxtalud = ref(10)
const error = ref('') // Error
const intentoValidar = ref(false) // Intento Validar

const errDovelasX = computed(
  () =>
    typeof dovelasXtalud.value !== 'number' ||
    dovelasXtalud.value % 1 !== 0 ||
    dovelasXtalud.value <= 0
)
const errDovelasAnchoMax = computed(
  () => typeof dovelasAnchoMaxtalud.value !== 'number' || dovelasAnchoMaxtalud.value <= 0
)
const errMetodo = computed(() => metodoTalud.value.length === 0)

// OBTIENE EL TALUD
function getTalud() {
  if (typeof props.idTalud === 'number' && props.idTalud !== 0) {
    axios.get('/api/talud/' + props.idTalud).then(function (response: { data: Talud10 }) {
      const { nombre, codigo, avance, sinCargas, dovelasX, dovelasAnchoMax, metodo } = response.data
      Object.assign(talud, { nombre, codigo, avance, sinCargas })
      if (avance >= NUMPASO) {
        dovelasXtalud.value = dovelasX as number
        dovelasAnchoMaxtalud.value = dovelasAnchoMax as number
        metodoTalud.value = (metodo as number).toString()
      } else {
        dovelasXtalud.value = 10
        dovelasAnchoMaxtalud.value = 10
        metodoTalud.value = ''
      }
    })
  }
}

// DESHACER
function deshacer() {
  getTalud()
}

// GUARDAR
function guardar() {
  if (errDovelasX.value || errDovelasAnchoMax.value || errMetodo.value) {
    intentoValidar.value = true
  } else {
    axios
      .put(
        '/api/paso' + NUMPASO + '/' + props.idTalud,
        {
          dovelasX: dovelasXtalud.value,
          dovelasAnchoMax: dovelasAnchoMaxtalud.value,
          metodo: Number.parseInt(metodoTalud.value)
        },
        {
          headers: { 'X-CSRF-TOKEN': getCookie('csrf_access_token') }
        }
      )
      .then(function () {
        getTalud()
      })
      .catch(function (errorAPI) {
        error.value = errorAPI.response.data.message
      })
  }
}

// ANALISIS
function analisis() {
  if (errDovelasX.value || errDovelasAnchoMax.value || errMetodo.value) {
    intentoValidar.value = true
  } else {
    axios
      .post(
        '/api/paso' + NUMPASO + '/' + props.idTalud,
        {
          dovelasX: dovelasXtalud.value,
          dovelasAnchoMax: dovelasAnchoMaxtalud.value,
          metodo: Number.parseInt(metodoTalud.value)
        },
        {
          headers: { 'X-CSRF-TOKEN': getCookie('csrf_access_token') }
        }
      )
      .then(function () {
        router.push('/paso' + (NUMPASO + 1) + '/' + props.idTalud)
      })
      .catch(function (errorAPI) {
        error.value = errorAPI.response.data.message
      })
  }
}

// ELIMINAR
function eliminar() {
  axios
    .delete('/api/paso' + NUMPASO + '/' + props.idTalud, {
      headers: { 'X-CSRF-TOKEN': getCookie('csrf_access_token') }
    })
    .then(function () {
      router.push('/paso' + (NUMPASO - 1) + '/' + props.idTalud)
    })
    .catch(function (errorAPI) {
      error.value = errorAPI.response.data.message
    })
}

// SE EJECUTA AL MONTAR LA VISTA
onMounted(getTalud)
</script>
