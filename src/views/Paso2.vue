<template>
  <div class="container-lg">
    <h1>{{ talud.nombre + ' - ' + TEXTOSPASOS[NUMPASO - 1] }}</h1>
    <pasos-talud :codigo="talud.codigo" :numpaso="NUMPASO" :pasos="pasos(talud)" />
    <h3 class="text-danger">{{ error }}</h3>
    <canvas id="canvas" :width="WIDTH" :height="HEIGHT" style="border: 1px solid black"></canvas>
    <h5 id="puntos" class="mt-3"></h5>
    <h5 v-if="talud.avance >= NUMPASO" class="mt-3">
      {{ textoPuntos(conTalud) }}
    </h5>
    <div class="d-flex align-items-start">
      <template v-if="talud.avance < NUMPASO">
        <div class="d-inline-block">
          <span class="h6">X:</span>
          <input
            v-model="nuevoPuntoX"
            type="text"
            class="me-2"
            :class="{ 'is-invalid': intentoValidar && errNuevoPuntoX }"
            style="width: 150px"
          />
          <div class="invalid-feedback">
            X entre {{ dimTalud.izquierda }} y {{ dimTalud.derecha }}
          </div>
        </div>
        <div class="d-inline-block">
          <span class="h6">Y:</span>
          <input
            v-model="nuevoPuntoY"
            type="text"
            class="me-2"
            :class="{ 'is-invalid': intentoValidar && errNuevoPuntoY }"
            style="width: 150px"
          />
          <div class="invalid-feedback">Y entre {{ dimTalud.abajo }} y {{ dimTalud.arriba }}</div>
        </div>
        <button @click="anadirPunto" type="button" class="btn btn-success btn-sm">
          Añadir punto
        </button>
      </template>
      <span id="puntoActual" class="h3 ms-3 mb-0"></span>
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
        Eliminar contorno
      </button>
      <button
        v-if="numObjetos > 0"
        @click="deshacerPunto"
        type="button"
        class="btn btn-warning btn-sm ms-3"
      >
        Deshacer último
      </button>
      <button
        v-if="talud.avance < NUMPASO && numObjetos >= PUNTOSMIN"
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
    </div>
  </div>
  <Modal v-model="muestraModal" :close="closeModal">
    <div class="modal">
      <p v-html="errorModal"></p>
      <button type="button" @click="closeModal" class="btn btn-outline-dark">cerrar</button>
    </div>
  </Modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, defineProps } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { getCookie } from '../functions/Cookie'
import { usePasos } from '../functions/Pasos'
import { taludBase, dimBase } from '../functions/Base'
import { useDibujo } from '../functions/Dibujo'
import { useGeometria } from '../functions/Geometria'
import type { Talud2, Punto } from '../types/talud'
import PasosTalud from '../components/PasosTalud.vue'

const props = defineProps({
  idTalud: Number
})

const router = useRouter()
const { TEXTOSPASOS, pasos } = usePasos()
const {
  iniciaDibujo,
  asignaGrosorYColor,
  getContorno,
  getPunto,
  textoPuntos,
  nuevoObjeto,
  eliminarUltimoObjeto,
  eventosDibujo,
  eventosGeneral,
  dibujaContorno,
  dibujaRegla
} = useDibujo()
const { interseccionaPolig } = useGeometria()
const NUMPASO = 2
const WIDTH = 820 // Pixels en eje X del area de dibujo
const HEIGHT = 560 // Pixels en eje Y del area de dibujo
const PUNTOSMIN = 2 // Número mínimo de puntos para guardar

const talud = reactive({ ...taludBase })
const conTalud = ref<Punto[]>([])
const dimTalud = reactive({ ...dimBase })
const nuevoPuntoX = ref('')
const nuevoPuntoY = ref('')
const numObjetos = ref(0)
const error = ref('') // Error
const intentoValidar = ref(false) // Intento Validar

const errorModal = ref('')
const muestraModal = ref(false)

const errNuevoPuntoX = computed(() => {
  const n = Number.parseFloat(nuevoPuntoX.value)
  return Number.isNaN(n) || n < dimTalud.izquierda || n > dimTalud.derecha
})

const errNuevoPuntoY = computed(() => {
  const n = Number.parseFloat(nuevoPuntoY.value)
  return Number.isNaN(n) || n < dimTalud.abajo || n > dimTalud.arriba
})

function openModal(err: string) {
  errorModal.value = err
  muestraModal.value = true
}

function closeModal() {
  muestraModal.value = false
}

// Comprueba que el punto (x,y) es válido para formar parte del contorno externo
function validoPuntoExterno(x: number, y: number) {
  // --- Descomentar este código si se quiere impedir volver atras en el eje X
  // let n = getContorno().length - 1
  // // La X debe ser superior o igual a la última X
  // let ok = n === -1 || x >= getPunto(n).x
  // ---
  let ok = true
  const n = numObjetos.value - 1
  if (n >= 0) {
    const { x: x0, y: y0 } = getPunto(n)
    ok = !interseccionaPolig(x0, y0, x, y, getContorno())
    if (!ok) openModal('El nuevo punto no puede producir una intersección')
  }
  return ok
}

// GESTIONA CANVAS
function gestionaCanvas() {
  dibujaRegla()
  asignaGrosorYColor(2, 'black')
  if (talud.avance < NUMPASO) {
    eventosDibujo('puntoActual', 'puntos', numObjetos, validoPuntoExterno)
  } else {
    dibujaContorno(conTalud.value)
  }
  eventosGeneral()
}

// OBTIENE EL TALUD Y GESTIONA CANVAS
function getTaludGestionaCanvas() {
  if (typeof props.idTalud === 'number' && props.idTalud !== 0) {
    axios.get('/api/talud/' + props.idTalud).then(function (response: { data: Talud2 }) {
      const { nombre, codigo, avance, sinCargas, dimensiones, contorno } = response.data
      Object.assign(talud, { nombre, codigo, avance, sinCargas })
      Object.assign(dimTalud, dimensiones)
      if (avance >= NUMPASO) {
        conTalud.value = contorno as Punto[]
      }
      iniciaDibujo('canvas', dimTalud, WIDTH, HEIGHT)
      gestionaCanvas()
    })
  }
}

// AL GUARDAR
function guardar() {
  axios
    .put(
      '/api/paso' + NUMPASO + '/' + props.idTalud,
      {
        contorno: getContorno()
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

// AL ELIMINAR
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

function deshacerPunto() {
  eliminarUltimoObjeto()
}

// AL AÑADIR PUNTO ESCRIBIENDO COORDENADAS
function anadirPunto() {
  if (errNuevoPuntoX.value || errNuevoPuntoY.value) {
    intentoValidar.value = true
  } else {
    const x = Number.parseFloat(nuevoPuntoX.value)
    const y = Number.parseFloat(nuevoPuntoY.value)
    if (validoPuntoExterno(x, y)) nuevoObjeto(x, y)
    intentoValidar.value = false
    nuevoPuntoX.value = ''
    nuevoPuntoY.value = ''
  }
}

// SE EJECUTA AL MONTAR LA VISTA
onMounted(getTaludGestionaCanvas)
</script>

<style scoped>
.modal {
  display: block;
  position: relative;
  height: auto;
  width: 480px;
  padding: 30px;
  box-sizing: border-box;
  background-color: #fff;
  font-size: 20px;
  text-align: center;
}
</style>
