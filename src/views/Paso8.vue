<template>
  <div class="container-lg">
    <h1>{{ talud.nombre + ' - ' + TEXTOSPASOS[NUMPASO - 1] }}</h1>
    <pasos-talud :codigo="talud.codigo" :numpaso="NUMPASO" :pasos="pasos(talud)" />
    <h3 class="text-danger">{{ error }}</h3>
    <canvas id="canvas" :width="WIDTH" :height="HEIGHT" style="border: 1px solid black"></canvas>
    <form class="mt-3">
      <div class="row mb-2">
        <div class="col-sm-6 col-lg-3 col-xl-2">
          <label for="numeroX" class="form-label">Núm. puntos en eje X</label>
          <input
            v-model.number="centrosTalud.numeroX"
            id="numeroX"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errNumeroX }"
          />
          <div class="invalid-feedback">Es necesario un número entero positivo</div>
        </div>
        <div class="col-sm-6 col-lg-3 col-xl-2">
          <label for="distanciaX" class="form-label">Distancia puntos en X</label>
          <input
            v-model.number="centrosTalud.distanciaX"
            id="distanciaX"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errDistanciaX }"
          />
          <div class="invalid-feedback">Es necesario un número positivo</div>
        </div>
        <div class="col-sm-6 col-lg-3 col-xl-2">
          <label for="numeroY" class="form-label">Núm. puntos en eje Y</label>
          <input
            v-model.number="centrosTalud.numeroY"
            id="numeroY"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errNumeroY }"
          />
          <div class="invalid-feedback">Es necesario un número entero positivo</div>
        </div>
        <div class="col-sm-6 col-lg-3 col-xl-2">
          <label for="distanciaY" class="form-label">Distancia puntos en Y</label>
          <input
            v-model.number="centrosTalud.distanciaY"
            id="distanciaY"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errDistanciaY }"
          />
          <div class="invalid-feedback">Es necesario un número positivo</div>
        </div>
      </div>
      <div class="row mb-2">
        <div class="col-sm-6 col-lg-3 col-xl-2">
          <label for="inicioX" class="form-label">X inferior izquierda</label>
          <input
            v-model.number="centrosTalud.inicioX"
            id="inicioX"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errInicioX }"
          />
          <div class="invalid-feedback">Es necesario un número</div>
        </div>
        <div class="col-sm-6 col-lg-3 col-xl-2">
          <label for="inicioY" class="form-label">Y inferior izquierda</label>
          <input
            v-model.number="centrosTalud.inicioY"
            id="inicioY"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errInicioY }"
          />
          <div class="invalid-feedback">Es necesario un número</div>
        </div>
        <div class="col-sm-6 col-lg-3 col-xl-2">
          <label for="desplazaX" class="form-label">Desplazamiento en X</label>
          <input
            v-model.number="centrosTalud.desplazaX"
            id="desplazaX"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errDesplazaX }"
          />
          <div class="invalid-feedback">Es necesario un número positivo</div>
        </div>
        <div class="col-sm-6 col-lg-3 col-xl-2">
          <label for="nradios" class="form-label">Número de radios</label>
          <input
            v-model.number="centrosTalud.nradios"
            id="nradios"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errNradios }"
          />
          <div class="invalid-feedback">Es necesario un número entero positivo (max. 10)</div>
        </div>
      </div>
    </form>
    <div class="my-3">
      <router-link to="/" class="btn btn-secondary btn-sm">Inicio</router-link>
      <router-link
        v-if="!talud.sinCargas"
        :to="'/paso' + (NUMPASO - 1) + '/' + talud.codigo"
        class="btn btn-secondary btn-sm ms-3"
        >Anterior</router-link
      >
      <router-link
        v-else
        :to="'/paso' + (NUMPASO - 2) + '/' + talud.codigo"
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
        v-if="talud.avance === NUMPASO"
        @click="deshacer"
        type="button"
        class="btn btn-warning btn-sm ms-3"
      >
        Deshacer
      </button>
      <button
        v-if="talud.avance <= NUMPASO"
        @click="guardar"
        type="button"
        class="btn btn-primary btn-sm ms-3"
      >
        Guardar
      </button>
      <router-link
        v-if="talud.avance >= NUMPASO"
        :to="'/paso' + (NUMPASO + 1) + '/' + talud.codigo"
        class="btn btn-secondary btn-sm ms-3"
        >Siguiente</router-link
      >
      <span id="puntoActual" class="h3 ms-3"></span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, defineProps } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { getCookie } from '../functions/Cookie'
import { usePasos } from '../functions/Pasos'
import { taludBase, dimBase, centrosBase } from '../functions/Base'
import { useDibujo } from '../functions/Dibujo'
import type { Talud8, Talud8r, Punto, Centros } from '../types/talud'
import PasosTalud from '../components/PasosTalud.vue'

const props = defineProps({
  idTalud: Number
})

const router = useRouter()
const { TEXTOSPASOS, pasos } = usePasos()
const {
  iniciaDibujo,
  limpiaDibujo,
  asignaGrosorYColor,
  eventosPunto,
  eventosGeneral,
  dibujaContorno,
  dibujaCentros,
  dibujaRegla
} = useDibujo()
const NUMPASO = 8
const WIDTH = 820 // Pixels en eje X del area de dibujo
const HEIGHT = 560 // Pixels en eje Y del area de dibujo
let conTalud: Punto[]

const dimTalud = { ...dimBase }

const talud = reactive({ ...taludBase })
const centrosTalud = reactive({ ...centrosBase })
const error = ref('') // Error
const intentoValidar = ref(false) // Intento Validar

const errNumeroX = computed(
  () =>
    typeof centrosTalud.numeroX !== 'number' ||
    centrosTalud.numeroX % 1 !== 0 ||
    centrosTalud.numeroX <= 0
)
const errNumeroY = computed(
  () =>
    typeof centrosTalud.numeroY !== 'number' ||
    centrosTalud.numeroY % 1 !== 0 ||
    centrosTalud.numeroY <= 0
)
const errDistanciaX = computed(
  () => typeof centrosTalud.distanciaX !== 'number' || centrosTalud.distanciaX <= 0
)
const errDistanciaY = computed(
  () => typeof centrosTalud.distanciaY !== 'number' || centrosTalud.distanciaY <= 0
)
const errInicioX = computed(() => typeof centrosTalud.inicioX !== 'number')
const errInicioY = computed(() => typeof centrosTalud.inicioY !== 'number')
const errDesplazaX = computed(
  () => typeof centrosTalud.desplazaX !== 'number' || centrosTalud.desplazaX < 0
)
const errNradios = computed(
  () =>
    typeof centrosTalud.nradios !== 'number' ||
    centrosTalud.nradios % 1 !== 0 ||
    centrosTalud.nradios <= 0 ||
    centrosTalud.nradios > 10
)

function asignaX(x: number) {
  centrosTalud.inicioX = x
}

function asignaY(y: number) {
  centrosTalud.inicioY = y
}

// GESTIONA CANVAS
function gestionaCanvas() {
  dibujaRegla()
  asignaGrosorYColor(2, 'black')
  dibujaContorno(conTalud)
  if (talud.avance >= NUMPASO) {
    asignaGrosorYColor(6, 'black')
    dibujaCentros(centrosTalud)
  } else {
    eventosPunto('puntoActual', asignaX, asignaY, (x, y) => true)
  }
  eventosGeneral()
}

// OBTIENE EL TALUD
function getTaludGestionaCanvas() {
  if (typeof props.idTalud === 'number' && props.idTalud !== 0) {
    axios.get('/api/talud/' + props.idTalud).then(function (response: { data: Talud8 }) {
      const { nombre, codigo, avance, sinCargas, dimensiones, contorno, centros } = response.data
      Object.assign(talud, { nombre, codigo, avance, sinCargas })
      Object.assign(dimTalud, dimensiones)
      conTalud = contorno as Punto[]
      if (avance >= NUMPASO) {
        Object.assign(centrosTalud, centros)
      } else {
        Object.assign(centrosTalud, { ...centrosBase })
      }
      iniciaDibujo('canvas', dimTalud, WIDTH, HEIGHT)
      gestionaCanvas()
    })
  }
}

function recargaTalud() {
  axios.get('/api/talud/' + props.idTalud).then(function (response: { data: Talud8r }) {
    const { avance, centros } = response.data
    talud.avance = avance
    if (avance >= NUMPASO) {
      Object.assign(centrosTalud, centros)
    } else {
      Object.assign(centrosTalud, { ...centrosBase })
    }
    // Reset valores
    intentoValidar.value = false
    //
    limpiaDibujo()
    gestionaCanvas()
  })
}

// DESHACER
function deshacer() {
  recargaTalud()
}

// GUARDAR
function guardar() {
  if (
    errNumeroX.value ||
    errNumeroY.value ||
    errDistanciaX.value ||
    errDistanciaY.value ||
    errInicioX.value ||
    errInicioY.value ||
    errDesplazaX.value ||
    errNradios.value
  ) {
    intentoValidar.value = true
  } else {
    axios
      .put(
        '/api/paso' + NUMPASO + '/' + props.idTalud,
        {
          centros: centrosTalud
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
onMounted(getTaludGestionaCanvas)
</script>
