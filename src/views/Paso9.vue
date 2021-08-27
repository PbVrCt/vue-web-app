<template>
  <div class="container-lg">
    <h1>{{ talud.nombre + ' - ' + TEXTOSPASOS[NUMPASO - 1] }}</h1>
    <pasos-talud :codigo="talud.codigo" :numpaso="NUMPASO" :pasos="pasos(talud)" />
    <h3 class="text-danger">{{ error }}</h3>
    <div class="row mt-3">
      <div class="col-lg-5">
        <form>
          <div class="row gx-1">
            <label class="col-3 form-label fw-bold">Centro</label>
            <label class="col-4 form-label">Min : Max</label>
            <label class="col-2 form-label fw-bold">R. Min.</label>
            <label class="col-2 form-label fw-bold">R. Max.</label>
          </div>
          <div v-for="(radio, ind) in radiosTalud" :key="radio.id" class="row gx-1 mb-1">
            <div class="col-3">{{ formatoCentro(radio) }}</div>
            <div class="col-4 text-muted">{{ radio.minCalc + ':' + radio.maxCalc }}</div>
            <div class="col-2">
              <input
                v-model.number="radio.min"
                :id="'min' + ind"
                required
                type="text"
                class="form-control form-control-sm"
                :class="{ 'is-invalid': intentoValidar && errRadioMin(radio) }"
              />
              <div class="invalid-feedback">No es válido</div>
            </div>
            <div class="col-2">
              <input
                v-model.number="radio.max"
                :id="'max' + ind"
                required
                type="text"
                class="form-control form-control-sm"
                :class="{ 'is-invalid': intentoValidar && errRadioMax(radio) }"
              />
              <div class="invalid-feedback">No es válido</div>
            </div>
            <div class="col-1">
              <button
                @click="muestra(radio)"
                type="button"
                class="btn btn-outline-secondary btn-sm"
              >
                Ver
              </button>
            </div>
          </div>
        </form>
      </div>
      <div class="col-lg-7">
        <canvas
          id="canvas"
          :width="WIDTH"
          :height="HEIGHT"
          style="border: 1px solid black"
        ></canvas>
      </div>
    </div>
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
        v-if="talud.avance >= NUMPASO"
        @click="deshacer"
        type="button"
        class="btn btn-warning btn-sm ms-3"
      >
        Deshacer
      </button>
      <button @click="guardar" type="button" class="btn btn-primary btn-sm ms-3">Guardar</button>
      <router-link
        v-if="talud.avance >= NUMPASO"
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
import { taludBase, dimBase, centrosBase } from '../functions/Base'
import { useDibujo } from '../functions/Dibujo'
import { COLORES } from '../functions/Colores'
import { useGeometria } from '../functions/Geometria'
import type { Talud9, Talud9r, Capa, Carga, Punto, Radios, Segmento } from '../types/talud'
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
  eventosGeneral,
  dibujaContorno,
  dibujaPunto,
  dibujaCentros,
  dibujaRadios,
  dibujaRegla
} = useDibujo()

const { recortaPoligono, calculaYenPoligono, distanciaPuntos, distanciaMinima, distanciaMaxima } =
  useGeometria()
const NUMPASO = 9
const WIDTH = 533 // Pixels en eje X del area de dibujo
const HEIGHT = 364 // Pixels en eje Y del area de dibujo
let conTalud: Punto[]
let capasTalud: Capa[]
let sinFreaticoTalud: boolean
let freaticoTalud: Punto[]
let cargasTalud: Carga[]

const dimTalud = { ...dimBase }

const talud = reactive({ ...taludBase })
const centrosTalud = reactive({ ...centrosBase })
const radiosTalud = ref<Radios[]>([])
const error = ref('') // Error
const intentoValidar = ref(false) // Intento Validar

const errRadioMin = (r: Radios) => typeof r.min !== 'number' || r.min < r.minCalc
const errRadioMax = (r: Radios) => typeof r.max !== 'number' || r.max > r.maxCalc * 10

function formatoCentro(r: Radios) {
  const numeros = r.id.split(' ')
  return '(' + numeros[0] + ',' + numeros[1] + ')'
}

// CALCULA RADIOS MINIMOS Y MAXIMOS
function calculaRadios() {
  const n = conTalud.length - 1
  let rMinCalc: number
  let rMaxCalc: number
  let rMin: number
  let rMax: number
  let rMin1: number
  let rMax1: number
  let inc: number
  let dist1: number
  let dist2: number
  let pun: Punto
  let seg: Segmento
  radiosTalud.value = []
  for (let ny = 0; ny < centrosTalud.numeroY; ++ny) {
    for (let nx = 0; nx < centrosTalud.numeroX; ++nx) {
      pun = {
        x: centrosTalud.inicioX + nx * centrosTalud.distanciaX + ny * centrosTalud.desplazaX,
        y: centrosTalud.inicioY + ny * centrosTalud.distanciaY
      }
      rMinCalc = Number.MAX_VALUE
      rMaxCalc = 0
      for (let i = 0; i < n; ++i) {
        seg = { x1: conTalud[i].x, y1: conTalud[i].y, x2: conTalud[i + 1].x, y2: conTalud[i + 1].y }
        rMin1 = distanciaMinima(pun, seg)
        rMax1 = distanciaMaxima(pun, seg)
        if (rMin1 < rMinCalc) rMinCalc = rMin1
        if (rMax1 > rMaxCalc) rMaxCalc = rMax1
      }
      rMinCalc = Math.ceil(rMinCalc * 100) / 100
      rMaxCalc = Math.floor(rMaxCalc * 100) / 100
      //
      if (centrosTalud.nradios === 1) {
        rMin = (rMaxCalc - rMinCalc) / 2
        rMax = rMin
      } else {
        // Calcula la distancia al extremo más cercano
        dist1 = distanciaPuntos(pun, conTalud[0])
        dist2 = distanciaPuntos(pun, conTalud[conTalud.length - 1])
        rMax = Math.min(dist1, dist2)
        if (rMax < rMinCalc) rMax = rMaxCalc // Medida de precaución
        // El radio mínimo ofrecido es el segundo considerando (NRadios + 1)
        inc = (rMax - rMinCalc) / centrosTalud.nradios // Equivale a (NRadios + 1)
        rMin = rMinCalc + inc
      }
      rMin = Math.ceil(rMin * 100) / 100
      rMax = Math.floor(rMax * 100) / 100
      radiosTalud.value.push({
        id: pun.x.toString() + ' ' + pun.y.toString(),
        min: rMin,
        max: rMax,
        minCalc: rMinCalc,
        maxCalc: rMaxCalc
      })
    }
  }
}

// MUESTRA RADIOS
function muestra(r: Radios) {
  const numeros = r.id.split(' ')
  const vX = Number.parseFloat(numeros[0])
  const vY = Number.parseFloat(numeros[1])
  limpiaDibujo()
  dibujaRegla()
  asignaGrosorYColor(2, 'black')
  dibujaContorno(conTalud)
  //
  let i = 0
  for (const cap of capasTalud) {
    asignaGrosorYColor(2, COLORES[i])
    dibujaContorno(cap.contorno)
    ++i
  }
  //
  if (!sinFreaticoTalud) {
    asignaGrosorYColor(2, 'black')
    dibujaContorno(freaticoTalud)
  }
  //
  if (!talud.sinCargas) {
    i = 0
    let cnt
    let y
    for (const car of cargasTalud) {
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
  //
  asignaGrosorYColor(6, 'black')
  dibujaCentros(centrosTalud)
  asignaGrosorYColor(6, 'red')
  dibujaPunto(vX, vY)
  asignaGrosorYColor(1, 'red')
  dibujaRadios(vX, vY, r.min, r.max, centrosTalud.nradios)
  eventosGeneral()
}

// GESTIONA CANVAS
function gestionaCanvas() {
  dibujaRegla()
  asignaGrosorYColor(2, 'black')
  dibujaContorno(conTalud)
  //
  let i = 0
  for (const cap of capasTalud) {
    asignaGrosorYColor(2, COLORES[i])
    dibujaContorno(cap.contorno)
    ++i
  }
  //
  if (!sinFreaticoTalud) {
    asignaGrosorYColor(2, 'black')
    dibujaContorno(freaticoTalud)
  }
  //
  if (!talud.sinCargas) {
    i = 0
    let cnt
    let y
    for (const car of cargasTalud) {
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
  //
  asignaGrosorYColor(6, 'black')
  dibujaCentros(centrosTalud)
  eventosGeneral()
}

// OBTIENE EL TALUD
function getTaludGestionaCanvas() {
  if (typeof props.idTalud === 'number' && props.idTalud !== 0) {
    axios.get('/api/talud/' + props.idTalud).then(function (response: { data: Talud9 }) {
      const {
        nombre,
        codigo,
        avance,
        sinCargas,
        dimensiones,
        contorno,
        capas,
        sinNivelFreatico,
        nivelFreatico,
        cargas,
        centros,
        radios
      } = response.data
      Object.assign(talud, { nombre, codigo, avance, sinCargas })
      Object.assign(dimTalud, dimensiones)
      conTalud = contorno as Punto[]
      capasTalud = capas as Capa[]
      sinFreaticoTalud = sinNivelFreatico as boolean
      freaticoTalud = nivelFreatico as Punto[]
      cargasTalud = cargas as Carga[]
      Object.assign(centrosTalud, centros)
      if (avance >= NUMPASO) {
        radiosTalud.value = radios as Radios[]
      } else {
        calculaRadios()
      }
      iniciaDibujo('canvas', dimTalud, WIDTH, HEIGHT)
      gestionaCanvas()
    })
  }
}

function recargaTalud() {
  intentoValidar.value = false
  axios.get('/api/talud/' + props.idTalud).then(function (response: { data: Talud9r }) {
    const { avance, radios } = response.data
    talud.avance = avance
    if (avance >= NUMPASO) {
      radiosTalud.value = radios as Radios[]
    } else {
      calculaRadios()
    }
    // Reset valores
    intentoValidar.value = false
  })
}

// DESHACER
function deshacer() {
  recargaTalud()
}

// GUARDAR
function guardar() {
  if (
    radiosTalud.value.some((r) => errRadioMin(r)) ||
    radiosTalud.value.some((r) => errRadioMax(r))
  ) {
    intentoValidar.value = true
  } else {
    // Para 3 radios se obtiene indicesRadios === [0,1,2]
    const indicesRadios = [...Array(radiosTalud.value.length).keys()]
    //
    axios
      .put(
        '/api/paso' + NUMPASO + '/' + props.idTalud,
        {
          radios: indicesRadios.map((i) => radiosTalud.value[i])
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
