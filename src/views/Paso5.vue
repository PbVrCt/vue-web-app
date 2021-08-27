<template>
  <div class="container-lg">
    <h1>{{ talud.nombre + ' - ' + TEXTOSPASOS[NUMPASO - 1] }}</h1>
    <pasos-talud :codigo="talud.codigo" :numpaso="NUMPASO" :pasos="pasos(talud)" />
    <h6>El primer y último punto deben coincidir con extremos del contorno</h6>
    <h3 class="text-danger">{{ error }}</h3>
    <canvas id="canvas" :width="WIDTH" :height="HEIGHT" style="border: 1px solid black"></canvas>
    <h5 v-if="talud.avance >= NUMPASO && sinFreaticoTalud && !modificando" class="mt-3">
      NO HAY NIVEL FREATICO PARA ESTE TALUD
    </h5>
    <h5 v-if="talud.avance < NUMPASO || modificando" class="mt-3">
      Extremos X del contorno: [ {{ extremoIzquierda }} a {{ extremoDerecha }} ]
    </h5>
    <h5 id="puntos" class="mt-3"></h5>
    <h5 v-if="talud.avance >= NUMPASO && !sinFreaticoTalud && !modificando" class="mt-3">
      {{ textoPuntos(freaticoTalud) }}
    </h5>
    <div class="d-flex align-items-start">
      <template v-if="talud.avance < NUMPASO || modificando">
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
        v-if="talud.avance === NUMPASO && !modificando"
        @click="eliminar"
        type="button"
        class="btn btn-danger btn-sm ms-3"
      >
        Eliminar
      </button>
      <button
        v-if="talud.avance >= NUMPASO && !modificando"
        @click="modificar"
        type="button"
        class="btn btn-warning btn-sm ms-3"
      >
        Modificar
      </button>
      <button
        v-if="talud.avance >= NUMPASO && modificando"
        @click="cancelar"
        type="button"
        class="btn btn-warning btn-sm ms-3"
      >
        Cancelar
      </button>
      <button
        v-if="numObjetos > 0"
        @click="deshacerPunto"
        type="button"
        class="btn btn-warning btn-sm ms-3"
      >
        Deshacer punto
      </button>
      <button
        v-if="(talud.avance < NUMPASO || modificando) && numObjetos === 0"
        @click="guardarSinFreatico"
        type="button"
        class="btn btn-warning btn-sm ms-3"
      >
        No hay nivel freático
      </button>
      <button
        v-if="(talud.avance < NUMPASO || modificando) && finalFreaticoValido"
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
import { COLORES } from '../functions/Colores'
import { useGeometria } from '../functions/Geometria'
import type { Talud5, Talud5r, Capa, Punto } from '../types/talud'
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
  textoPuntos,
  nuevoObjeto,
  eliminarUltimoObjeto,
  eventosDibujo,
  eventosGeneral,
  dibujaContorno,
  dibujaRegla
} = useDibujo()
const { porDebajoPolig, porEncimaPolig, interseccionaPolig } = useGeometria()
const NUMPASO = 5
const WIDTH = 820 // Pixels en eje X del area de dibujo
const HEIGHT = 560 // Pixels en eje Y del area de dibujo
let conTalud: Punto[]
let capasTalud: Capa[]

const talud = reactive({ ...taludBase })
const dimTalud = reactive({ ...dimBase })
const sinFreaticoTalud = ref(false)
const freaticoTalud = ref<Punto[]>([])
const modificando = ref(false)
const nuevoPuntoX = ref('')
const nuevoPuntoY = ref('')
const numObjetos = ref(0)
const extremoIzquierda = ref(0)
const extremoDerecha = ref(0)
const error = ref('') // Error
const finalFreaticoValido = ref(false)
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

// Comprueba que 'porEncimaPolig' devuelve true para todo
function porEncimaTodosFreatico(x1: number, y1: number, x2: number, y2: number) {
  const polig = [
    { x: x1, y: y1 },
    { x: x2, y: y2 }
  ]
  let ok = true
  // Comprueba el contorno externo
  for (const { x, y } of conTalud) {
    if (ok) ok = porEncimaPolig(polig, x, y, true)
  }
  return ok
}

// Comprueba que el punto (x,y) es válido para formar parte del nivel freático
function validoPuntoFreatico(x: number, y: number) {
  // --- Descomentar este código si se quiere impedir volver atras en el eje X
  // let n = getContorno().length - 1
  // // La X debe ser superior o igual a la última X
  // let ok = n === -1 || x >= getPunto(n).x
  // ---
  let n = conTalud.length - 1
  // La X debe estar contenida en el intervalo del eje X definido por el contorno externo
  let ok = x >= conTalud[0].x && x <= conTalud[n].x
  if (!ok) {
    if (numObjetos.value === 0) {
      openModal('La X del primer punto debe ser ' + conTalud[0].x)
    } else {
      openModal('La X debe estar entre ' + conTalud[0].x + ' y ' + conTalud[n].x)
    }
  } else {
    n = numObjetos.value - 1
  }
  //
  if (ok) {
    // La Y no puede ser superior al contorno
    ok = porDebajoPolig(conTalud, x, y, false)
    if (!ok) openModal('La Y no puede ser superior al contorno externo')
  }
  if (ok) {
    if (numObjetos.value === 0) {
      // El primer punto: Su X debe ser igual a la del primero punto del contorno externo
      ok = x === conTalud[0].x
      if (!ok) openModal('La X del primer punto debe ser ' + conTalud[0].x)
    } else {
      // Todos los puntos de contorno externo deben estar por encima del segmento definido por el ultimo punto
      const { x: x0, y: y0 } = getPunto(n)
      ok = porEncimaTodosFreatico(x0, y0, x, y)
      if (!ok) openModal('La Y no puede ser superior al contorno externo')
      if (ok) {
        ok = !interseccionaPolig(x0, y0, x, y, getContorno())
        if (!ok) openModal('El nuevo punto no puede producir una intersección')
      }
    }
  }
  finalFreaticoValido.value = ok && x === extremoDerecha.value
  return ok
}

// GESTIONA CANVAS
function gestionaCanvas() {
  dibujaRegla()
  asignaGrosorYColor(2, 'black')
  dibujaContorno(conTalud)
  let i = 0
  for (const cap of capasTalud) {
    asignaGrosorYColor(2, COLORES[i])
    dibujaContorno(cap.contorno)
    ++i
  }
  if (modificando.value) {
    asignaGrosorYColor(4, 'black')
    eventosDibujo('puntoActual', 'puntos', numObjetos, validoPuntoFreatico)
  } else {
    if (talud.avance >= NUMPASO && !sinFreaticoTalud.value) {
      asignaGrosorYColor(4, 'black')
      dibujaContorno(freaticoTalud.value)
    } else if (talud.avance < NUMPASO) {
      asignaGrosorYColor(4, 'black')
      eventosDibujo('puntoActual', 'puntos', numObjetos, validoPuntoFreatico)
    }
  }
  eventosGeneral()
}

// OBTIENE EL TALUD Y GESTIONA CANVAS
function getTaludGestionaCanvas() {
  if (typeof props.idTalud === 'number' && props.idTalud !== 0) {
    axios.get('/api/talud/' + props.idTalud).then(function (response: { data: Talud5 }) {
      const {
        nombre,
        codigo,
        avance,
        sinCargas,
        dimensiones,
        contorno,
        capas,
        sinNivelFreatico,
        nivelFreatico
      } = response.data
      Object.assign(talud, { nombre, codigo, avance, sinCargas })
      Object.assign(dimTalud, dimensiones)
      conTalud = contorno
      capasTalud = capas
      modificando.value = false
      extremoIzquierda.value = conTalud[0].x
      extremoDerecha.value = conTalud[conTalud.length - 1].x
      if (avance >= NUMPASO) {
        sinFreaticoTalud.value = sinNivelFreatico as boolean
        freaticoTalud.value = nivelFreatico as Punto[]
      }
      iniciaDibujo('canvas', dimTalud, WIDTH, HEIGHT)
      gestionaCanvas()
    })
  }
}

function recargaTalud() {
  axios.get('/api/talud/' + props.idTalud).then(function (response: { data: Talud5r }) {
    const { avance, sinNivelFreatico, nivelFreatico } = response.data
    talud.avance = avance
    if (avance >= NUMPASO) {
      sinFreaticoTalud.value = sinNivelFreatico as boolean
      freaticoTalud.value = nivelFreatico as Punto[]
    } else {
      sinFreaticoTalud.value = false
      freaticoTalud.value = []
    }
    // Reset valores
    finalFreaticoValido.value = false
    intentoValidar.value = false
    modificando.value = false
    nuevoPuntoX.value = ''
    nuevoPuntoY.value = ''
    numObjetos.value = 0
    //
    limpiaDibujo()
    gestionaCanvas()
  })
}

// AL GUARDAR
function guardar() {
  axios
    .put(
      '/api/paso' + NUMPASO + '/' + props.idTalud,
      {
        nivelFreatico: getContorno()
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

function guardarSinFreatico() {
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

// AL MODIFICAR
function modificar() {
  limpiaDibujo()
  modificando.value = true
  numObjetos.value = 0
  gestionaCanvas()
}

// AL CANCELAR
function cancelar() {
  limpiaDibujo()
  modificando.value = false
  numObjetos.value = 0
  gestionaCanvas()
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
    if (validoPuntoFreatico(x, y)) nuevoObjeto(x, y)
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
