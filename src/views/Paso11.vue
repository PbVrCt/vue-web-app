<template>
  <div class="container-lg">
    <h1>{{ talud.nombre + ' - ' + TEXTOSPASOS[NUMPASO - 1] }}</h1>
    <pasos-talud :codigo="talud.codigo" :numpaso="NUMPASO" :pasos="pasos(talud)" />
    <h3 class="text-danger">{{ error }}</h3>
    <div class="row">
      <div class="col-lg-7 col-xl-6 col-xxl-5">
        <canvas
          id="canvas"
          :width="WIDTH"
          :height="HEIGHT"
          style="border: 1px solid black"
        ></canvas>
      </div>
      <div class="col-lg-5 col-xl-4 col-xxl-3">
        <a :href="'/grafico/' + talud.codigo" target="_blank">
          <img :src="graficaAnalisis" :width="376" :height="364" />
        </a>
      </div>
    </div>
    <div class="row mt-3">
      <h5 class="col-lg-3">Centro: ({{ centroRadioTalud.x }},{{ centroRadioTalud.y }})</h5>
      <h5 class="col-lg-3">Radio: {{ Math.round(radioTalud * 100) / 100 }}</h5>
      <h5 class="col-lg-3">Coeficiente: {{ Math.round(coefTalud * 1000000) / 1000000 }}</h5>
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
        Eliminar
      </button>
    </div>
    <div class="row mb-3">
      <div class="col-lg-4">
        <table class="table table-sm table-borderless">
          <thead>
            <tr>
              <th scope="col">Centro</th>
              <th scope="col">Radio</th>
              <th scope="col">Coef.</th>
            </tr>
          </thead>
          <tbody v-for="coef in coeficientesTalud" :key="coef.coeficiente">
            <tr>
              <td>{{ '(' + coef.centroX + ',' + coef.centroY + ')' }}</td>
              <td>{{ Math.round(coef.radio * 100) / 100 }}</td>
              <td>{{ Math.round(coef.coeficiente * 1000000) / 1000000 }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, defineProps } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { getCookie } from '../functions/Cookie'
import { usePasos } from '../functions/Pasos'
import { puntoBase, taludBase, dimBase, centrosBase } from '../functions/Base'
import { useDibujo } from '../functions/Dibujo'
import { COLORES } from '../functions/Colores'
import { useGeometria } from '../functions/Geometria'
import type { Talud11, Capa, Carga, Punto, DatosCoef } from '../types/talud'
import PasosTalud from '../components/PasosTalud.vue'

const props = defineProps({
  idTalud: Number
})

const router = useRouter()
const { TEXTOSPASOS, pasos } = usePasos()
const {
  iniciaDibujo,
  asignaGrosorYColor,
  eventosGeneral,
  dibujaContorno,
  dibujaPunto,
  dibujaCentros,
  dibujaRadio,
  dibujaRegla
} = useDibujo()

const { recortaPoligono, calculaYenPoligono } = useGeometria()
const NUMPASO = 11
const WIDTH = 533 // Pixels en eje X del area de dibujo
const HEIGHT = 364 // Pixels en eje Y del area de dibujo
let conTalud: Punto[]
let capasTalud: Capa[]
let sinFreaticoTalud: boolean
let freaticoTalud: Punto[]
let cargasTalud: Carga[]

const centrosTalud = reactive({ ...centrosBase })
const centroRadioTalud = { ...puntoBase }
const radioTalud = ref(0)
const coefTalud = ref(0)
const coeficientesTalud = ref<DatosCoef[]>([])

const dimTalud = { ...dimBase }
const talud = reactive({ ...taludBase })

const error = ref('') // Error

// const graficaAnalisis = ref<ArrayBuffer>()
const graficaAnalisis = ref<string>()

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
  //
  asignaGrosorYColor(6, 'red')
  dibujaPunto(centroRadioTalud.x, centroRadioTalud.y)
  asignaGrosorYColor(1, 'red')
  dibujaRadio(centroRadioTalud.x, centroRadioTalud.y, radioTalud.value)
  eventosGeneral()
}

// OBTIENE EL TALUD
function getTaludGestionaCanvas() {
  if (typeof props.idTalud === 'number' && props.idTalud !== 0) {
    axios.get('/api/talud/' + props.idTalud).then(function (response: { data: Talud11 }) {
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
        analisis
      } = response.data
      Object.assign(talud, { nombre, codigo, avance, sinCargas })
      Object.assign(dimTalud, dimensiones)
      conTalud = contorno as Punto[]
      capasTalud = capas as Capa[]
      sinFreaticoTalud = sinNivelFreatico as boolean
      freaticoTalud = nivelFreatico as Punto[]
      cargasTalud = cargas as Carga[]
      Object.assign(centrosTalud, centros)
      Object.assign(centroRadioTalud, { x: analisis.centroX, y: analisis.centroY })
      radioTalud.value = analisis.radio
      coefTalud.value = analisis.coefMin
      coeficientesTalud.value = analisis.coeficientes as DatosCoef[]
      // preparaDatosPlotly()
      iniciaDibujo('canvas', dimTalud, WIDTH, HEIGHT)
      gestionaCanvas()
    })
    //
    axios.get('/api/graf1/' + props.idTalud, { responseType: 'blob' }).then((response) => {
      const reader = new FileReader()
      reader.readAsDataURL(response.data)
      reader.onload = () => {
        // graficaAnalisis.value = reader.result as ArrayBuffer
        graficaAnalisis.value = reader.result as string
      }
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
