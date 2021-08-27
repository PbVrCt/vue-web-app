<template>
  <div class="container-lg">
    <h1>{{ talud.nombre + ' - ' + TEXTOSPASOS[NUMPASO - 1] }}</h1>
    <pasos-talud :codigo="talud.codigo" :numpaso="NUMPASO" :pasos="pasos(talud)" />
    <h3 class="text-danger">{{ error }}</h3>
    <canvas id="canvas" :width="WIDTH" :height="HEIGHT" style="border: 1px solid black"></canvas>
    <h5 v-if="talud.avance >= NUMPASO && talud.sinCargas" class="mt-3">
      NO HAY CARGAS EN ESTE TALUD
    </h5>
    <template v-if="talud.avance > NUMPASO">
      <h5 v-for="carga in cargasTalud" :key="carga.nombre" class="mt-3">
        {{ carga.nombre }}: {{ textoIntervalo(carga.xInicial, carga.xFinal) }}
      </h5>
    </template>
    <div class="d-flex align-items-start mt-3">
      <template v-if="talud.avance < NUMPASO || (talud.avance === NUMPASO && !talud.sinCargas)">
        <div class="d-inline-block">
          <span class="h6">Nombre: </span>
          <input
            v-model="nombreCarga"
            type="text"
            class="me-2"
            :class="{ 'is-invalid': intentoValidar && errNombreCarga }"
            style="width: 140px"
          />
          <div class="invalid-feedback">Es necesario un nombre</div>
        </div>
        <div class="d-inline-block">
          <span class="h6">X inicial: </span>
          <input
            v-model="puntoXi"
            type="text"
            class="me-2"
            :class="{ 'is-invalid': intentoValidar && errPuntoXi }"
            style="width: 140px"
          />
          <div class="invalid-feedback">X fuera de intervalo o coincide</div>
        </div>
        <div class="d-inline-block">
          <span class="h6">X final: </span>
          <input
            v-model="puntoXf"
            type="text"
            class="me-2"
            :class="{ 'is-invalid': intentoValidar && errPuntoXf }"
            style="width: 140px"
          />
          <div class="invalid-feedback">X fuera de intervalo o coincide</div>
        </div>
        <button @click="guardar" type="button" class="btn btn-success btn-sm">Guardar carga</button>
      </template>
    </div>
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
        {{ talud.sinCargas ? 'Quitar restricción (sin cargas)' : 'Eliminar última carga' }}
      </button>
      <button
        v-if="talud.avance < NUMPASO"
        @click="guardarSinCargas"
        type="button"
        class="btn btn-warning btn-sm ms-3"
      >
        No hay cargas
      </button>
      <router-link
        v-if="talud.avance >= NUMPASO && !talud.sinCargas"
        :to="'/paso' + (NUMPASO + 1) + '/' + talud.codigo"
        class="btn btn-secondary btn-sm ms-3"
        >Siguiente</router-link
      >
      <router-link
        v-if="talud.avance >= NUMPASO && talud.sinCargas"
        :to="'/paso' + (NUMPASO + 2) + '/' + talud.codigo"
        class="btn btn-secondary btn-sm ms-3"
        >Siguiente</router-link
      >
      <span id="puntoActual" class="h3 ms-3 mb-0"></span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, defineProps } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { getCookie } from '../functions/Cookie'
import { usePasos } from '../functions/Pasos'
import { taludBase, dimBase } from '../functions/Base'
import { useDibujo } from '../functions/Dibujo'
import { COLORES } from '../functions/Colores'
import { useGeometria } from '../functions/Geometria'
import type { Talud6, Talud6r, Punto, Carga } from '../types/talud'
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
  getContorno,
  getPunto,
  textoIntervalo,
  nuevoObjeto,
  eliminarUltimoObjeto,
  eventosIntervalo,
  eventosGeneral,
  dibujaContorno,
  dibujaRegla
} = useDibujo()
const { recortaPoligono, calculaYenPoligono } = useGeometria()
const NUMPASO = 6
const WIDTH = 820 // Pixels en eje X del area de dibujo
const HEIGHT = 560 // Pixels en eje Y del area de dibujo
let conTalud: Punto[]

const talud = reactive({ ...taludBase })
const dimTalud = reactive({ ...dimBase })
const cargasTalud = ref<Carga[]>([])
const numObjetos = ref(0)
const nombreCarga = ref('')
const puntoXi = ref('')
const puntoXf = ref('')
const error = ref('') // Error
const intentoValidar = ref(false) // Intento Validar

function coincideCarga(xi: number, xf: number) {
  let err = false
  let i = 0
  const n = cargasTalud.value.length
  while (!err && i < n) {
    err = xi < cargasTalud.value[i].xFinal && xf > cargasTalud.value[i].xInicial
    if (!err) ++i
  }
  return err
}

const errPuntoXi = computed(() => {
  let xi = Number.parseFloat(puntoXi.value)
  let xf = Number.parseFloat(puntoXf.value)
  let err = false
  if (Number.isNaN(xi)) err = true
  if (!err && (xi < dimTalud.izquierda || xi > dimTalud.derecha)) err = true
  if (!err && !Number.isNaN(xf)) {
    if (xf < xi) [xi, xf] = [xf, xi] // Intercambiar valores si xf < xi
    err = coincideCarga(xi, xf)
  }
  return err
})

const errPuntoXf = computed(() => {
  let xi = Number.parseFloat(puntoXi.value)
  let xf = Number.parseFloat(puntoXf.value)
  let err = false
  if (Number.isNaN(xf)) err = true
  if (!err && (xf < dimTalud.izquierda || xf > dimTalud.derecha)) err = true
  if (!err && !Number.isNaN(xi)) {
    if (xf < xi) [xi, xf] = [xf, xi] // Intercambiar valores si xf < xi
    err = coincideCarga(xi, xf)
  }
  return err
})

const errNombreCarga = computed(() => nombreCarga.value.length === 0)

function asignaXi(xi: string) {
  puntoXi.value = xi
}

function asignaXf(xf: string) {
  puntoXf.value = xf
}

// GESTIONA CANVAS
function gestionaCanvas() {
  dibujaRegla()
  asignaGrosorYColor(2, 'black')
  dibujaContorno(conTalud)
  if (talud.avance >= NUMPASO && !talud.sinCargas) {
    let i = 0
    let cnt
    let y
    for (const car of cargasTalud.value) {
      asignaGrosorYColor(6, COLORES[i])
      if (car.xFinal !== car.xInicial) {
        cnt = recortaPoligono(conTalud, car.xInicial, car.xFinal)
        dibujaContorno(cnt)
      } else {
        y = calculaYenPoligono(conTalud, car.xInicial)
        dibujaContorno([{ x: car.xInicial, y: y }])
      }
      ++i
    }
  }
  if (talud.avance < NUMPASO || (talud.avance === NUMPASO && !talud.sinCargas)) {
    eventosIntervalo('puntoActual', asignaXi, asignaXf, (x) => true)
  }
  eventosGeneral()
}

// OBTIENE EL TALUD Y GESTIONA CANVAS
function getTaludGestionaCanvas() {
  if (typeof props.idTalud === 'number' && props.idTalud !== 0) {
    axios.get('/api/talud/' + props.idTalud).then(function (response: { data: Talud6 }) {
      const { nombre, codigo, avance, sinCargas, dimensiones, contorno, cargas } = response.data
      Object.assign(talud, { nombre, codigo, avance, sinCargas })
      Object.assign(dimTalud, dimensiones)
      conTalud = contorno as Punto[]
      if (avance >= NUMPASO) {
        cargasTalud.value = cargas as Carga[]
      }
      iniciaDibujo('canvas', dimTalud, WIDTH, HEIGHT)
      gestionaCanvas()
    })
  }
}

function recargaTalud() {
  axios.get('/api/talud/' + props.idTalud).then(function (response: { data: Talud6r }) {
    const { avance, sinCargas, cargas } = response.data
    talud.avance = avance
    talud.sinCargas = sinCargas
    if (avance >= NUMPASO) {
      cargasTalud.value = cargas as Carga[]
    } else {
      cargasTalud.value = []
    }
    // Reset valores
    intentoValidar.value = false
    nombreCarga.value = ''
    puntoXi.value = ''
    puntoXf.value = ''
    numObjetos.value = 0
    //
    limpiaDibujo()
    gestionaCanvas()
  })
}

// AL GUARDAR
function guardar() {
  if (errNombreCarga.value || errPuntoXi.value || errPuntoXf.value) {
    intentoValidar.value = true
  } else {
    let vXi = Number.parseFloat(puntoXi.value)
    let vXf = Number.parseFloat(puntoXf.value)
    if (vXf < vXi) [vXi, vXf] = [vXf, vXi] // Intercambiar valores si vXf < vXi
    axios
      .put(
        '/api/paso' + NUMPASO + '/' + props.idTalud,
        {
          nombre: nombreCarga.value,
          xInicial: vXi,
          xFinal: vXf
        },
        {
          headers: { 'X-CSRF-TOKEN': getCookie('csrf_access_token') }
        }
      )
      .then(function () {
        recargaTalud()
      })
      .catch(function (errorAPI) {
        error.value = errorAPI.response.data.message
      })
  }
}

function guardarSinCargas() {
  axios
    .post('/api/paso' + NUMPASO + '/' + props.idTalud, null, {
      headers: { 'X-CSRF-TOKEN': getCookie('csrf_access_token') }
    })

    .then(function () {
      recargaTalud()
    })
    .catch(function (errorAPI) {
      error.value = errorAPI.response.data.message
    })
}

// AL ELIMINAR
function eliminar() {
  axios
    .delete('/api/paso' + NUMPASO + '/' + props.idTalud, {
      headers: { 'X-CSRF-TOKEN': getCookie('csrf_access_token') }
    })
    .then(function () {
      recargaTalud()
    })
    .catch(function (errorAPI) {
      error.value = errorAPI.response.data.message
    })
}

// SE EJECUTA AL MONTAR LA VISTA
onMounted(getTaludGestionaCanvas)
</script>
