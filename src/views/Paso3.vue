<template>
  <div class="container-lg">
    <h1>{{ talud.nombre + ' - ' + TEXTOSPASOS[NUMPASO - 1] }}</h1>
    <pasos-talud :codigo="talud.codigo" :numpaso="NUMPASO" :pasos="pasos(talud)" />
    <h6>Las capas deben añadirse de arriba a abajo</h6>
    <h6>
      El primer y último punto deben coincidir con extremos del contorno o estar en otra capa o
      contorno
    </h6>
    <h6>
      Para marcar puntos en otras capas deben ser vertices o estar en segmentos horizontales o
      verticales
    </h6>
    <h3 class="text-danger">{{ error }}</h3>
    <canvas id="canvas" :width="WIDTH" :height="HEIGHT" style="border: 1px solid black"></canvas>
    <h5 v-if="talud.avance >= NUMPASO && sinCapasTalud" class="mt-3">
      ESTE TALUD ES HOMOGENEO (SIN CAPAS)
    </h5>
    <h5
      v-else-if="talud.avance < NUMPASO || (talud.avance === NUMPASO && !sinCapasTalud)"
      class="mt-3"
    >
      Extremos X del contorno: [ {{ extremoIzquierda }} a {{ extremoDerecha }} ]
    </h5>
    <h5 id="puntos" class="mt-3"></h5>
    <template v-if="talud.avance > NUMPASO">
      <h5 v-for="capa in capasTalud" :key="capa.nombre" class="mt-3">
        {{ capa.nombre }}: {{ textoPuntos(capa.contorno) }}
      </h5>
    </template>
    <div class="d-flex align-items-start">
      <template v-if="talud.avance < NUMPASO || (talud.avance === NUMPASO && !sinCapasTalud)">
        <div class="d-inline-block">
          <span class="h6">X:</span>
          <input
            v-model="nuevoPuntoX"
            type="text"
            class="me-2"
            :class="{ 'is-invalid': intentoValidarPunto && errNuevoPuntoX }"
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
            :class="{ 'is-invalid': intentoValidarPunto && errNuevoPuntoY }"
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
    <div
      v-if="
        (talud.avance < NUMPASO || (talud.avance === NUMPASO && !sinCapasTalud)) && finalCapaValido
      "
      class="d-flex align-items-start mt-3"
    >
      <div class="d-inline-block">
        <span class="h6">Material:</span>
        <input
          v-model="nombreCapa"
          type="text"
          :class="{ 'is-invalid': intentoValidarCapa && errNombreCapa }"
          style="width: 150px"
        />
        <div class="invalid-feedback">Es necesario un nompre de capa</div>
      </div>
      <button @click="guardar" type="button" class="btn btn-primary btn-sm ms-3">
        Guardar capa
      </button>
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
        {{ sinCapasTalud ? 'Quitar restricción (sin capas)' : 'Eliminar última capa' }}
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
        v-if="talud.avance < NUMPASO && numObjetos === 0"
        @click="guardarSinCapas"
        type="button"
        class="btn btn-warning btn-sm ms-3"
      >
        No hay capas
      </button>
      <router-link
        v-if="talud.avance >= NUMPASO"
        :to="'/paso' + (NUMPASO + 1) + '/' + talud.codigo"
        class="btn btn-secondary btn-sm ms-3"
        >Siguiente</router-link
      >
    </div>
    <h5 v-if="talud.avance <= NUMPASO" class="mt-3">exterior: {{ textoPuntos(conTalud) }}</h5>
    <template v-if="talud.avance === NUMPASO">
      <h5 v-for="capa in capasTalud" :key="capa.nombre">
        {{ capa.nombre }}: {{ textoPuntos(capa.contorno) }}
      </h5>
    </template>
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
import type { Talud3, Talud3r, Punto, Capa } from '../types/talud'
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
const { enSegmentoPolig, porDebajoPolig, porEncimaPolig, interseccionaPolig } = useGeometria()
const NUMPASO = 3
const WIDTH = 820 // Pixels en eje X del area de dibujo
const HEIGHT = 560 // Pixels en eje Y del area de dibujo
const conTalud = ref<Punto[]>([])

const talud = reactive({ ...taludBase })
const dimTalud = reactive({ ...dimBase })
const sinCapasTalud = ref(false)
const capasTalud = ref<Capa[]>([])
const nuevoPuntoX = ref('')
const nuevoPuntoY = ref('')
const numObjetos = ref(0)
const extremoIzquierda = ref(0)
const extremoDerecha = ref(0)
const nombreCapa = ref('')
const error = ref('')
const finalCapaValido = ref(false)
const intentoValidarPunto = ref(false)
const intentoValidarCapa = ref(false)

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

const errNombreCapa = computed(() => nombreCapa.value.length === 0)

function openModal(err: string) {
  errorModal.value = err
  muestraModal.value = true
}

function closeModal() {
  muestraModal.value = false
}

// Comprueba que 'enSegmentoPolig' devuelve true para alguna capa o contorno externo
function enSegmentoCualquiera(x: number, y: number) {
  let ok = enSegmentoPolig(conTalud.value, x, y)
  let i = 0
  while (!ok && i < capasTalud.value.length) {
    ok = enSegmentoPolig(capasTalud.value[i].contorno, x, y)
    if (!ok) ++i
  }
  return ok
}

// Comprueba que 'porDebajoPolig' devuelve true para todas las capas y para el contorno externo
function porDebajoTodosCapa(x: number, y: number) {
  // Comprueba el contorno externo
  let ok = porDebajoPolig(conTalud.value, x, y, false)
  let i = 0
  // Comprueba todas las capas anteriores/superiores
  while (ok && i < capasTalud.value.length) {
    ok = porDebajoPolig(capasTalud.value[i].contorno, x, y, true)
    if (ok) ++i
  }
  return ok
}

// Comprueba que 'porEncimaPolig' devuelve true para todo
function porEncimaTodosCapa(x1: number, y1: number, x2: number, y2: number) {
  const polig = [
    { x: x1, y: y1 },
    { x: x2, y: y2 }
  ]
  let ok = true
  // Comprueba el contorno externo
  for (const { x, y } of conTalud.value) {
    if (ok) ok = porEncimaPolig(polig, x, y, true)
  }
  let i = 0
  // Comprueba todas las capas anteriores/superiores
  while (ok && i < capasTalud.value.length) {
    for (const { x, y } of capasTalud.value[i].contorno) {
      if (ok) ok = porEncimaPolig(polig, x, y, true)
    }
    if (ok) ++i
  }
  return ok
}

// Comprueba que el punto (x,y) es válido para formar parte de la última capa
function validoPuntoCapa(x: number, y: number) {
  let n = conTalud.value.length - 1
  // La X debe estar contenida en el intervalo del eje X definido por el contorno externo
  let ok = x >= conTalud.value[0].x && x <= conTalud.value[n].x
  if (!ok) {
    if (numObjetos.value === 0) {
      openModal(
        'La X del primer punto debe ser ' +
          conTalud.value[0].x +
          '<br />o bien un vertice o un punto en un segmento horizontal o vertical de la capa anterior'
      )
    } else {
      openModal('La X debe estar entre ' + conTalud.value[0].x + ' y ' + conTalud.value[n].x)
    }
  } else {
    n = numObjetos.value - 1
  }
  //
  if (ok) {
    // La Y no puede ser superior a ninguna capa o contorno
    ok = porDebajoTodosCapa(x, y)
    if (!ok) openModal('La Y no puede ser superior a ninguna capa o contorno externo')
  }
  if (ok) {
    if (numObjetos.value === 0) {
      // El primer punto: Debe estar contenido o su X debe ser igual a la del primero punto del contorno externo
      ok = x === conTalud.value[0].x || enSegmentoCualquiera(x, y)
      if (!ok) {
        openModal(
          'La X del primer punto debe ser ' +
            conTalud.value[0].x +
            '<br />o bien un vertice o un punto en un segmento horizontal o vertical de la capa anterior'
        )
      }
    } else {
      // Todos los puntos de contorno y capas deben estar por encima del segmento definido por el ultimo punto
      const { x: x0, y: y0 } = getPunto(n)
      ok = porEncimaTodosCapa(x0, y0, x, y)
      if (!ok) openModal('La Y no puede ser superior a ninguna capa o contorno externo')
      if (ok) {
        ok = !interseccionaPolig(x0, y0, x, y, getContorno())
        if (!ok) openModal('El nuevo punto no puede producir una intersección')
      }
    }
  }
  finalCapaValido.value =
    ok && (x === extremoDerecha.value || (numObjetos.value > 0 && enSegmentoCualquiera(x, y)))
  return ok
}

// GESTIONA CANVAS
function gestionaCanvas() {
  dibujaRegla()
  asignaGrosorYColor(2, 'black')
  dibujaContorno(conTalud.value)
  if (talud.avance >= NUMPASO && !sinCapasTalud.value) {
    let i = 0
    for (const cap of capasTalud.value) {
      asignaGrosorYColor(2, COLORES[i])
      dibujaContorno(cap.contorno)
      ++i
    }
  }
  if (talud.avance < NUMPASO || (talud.avance === NUMPASO && !sinCapasTalud.value)) {
    asignaGrosorYColor(4, 'black')
    eventosDibujo('puntoActual', 'puntos', numObjetos, validoPuntoCapa)
  }
  eventosGeneral()
}

// OBTIENE EL TALUD Y GESTIONA CANVAS
function getTaludGestionaCanvas() {
  if (typeof props.idTalud === 'number' && props.idTalud !== 0) {
    axios.get('/api/talud/' + props.idTalud).then(function (response: { data: Talud3 }) {
      const { nombre, codigo, avance, sinCargas, dimensiones, contorno, sinCapas, capas } =
        response.data
      Object.assign(talud, { nombre, codigo, avance, sinCargas })
      Object.assign(dimTalud, dimensiones)
      conTalud.value = contorno as Punto[]
      extremoIzquierda.value = conTalud.value[0].x
      extremoDerecha.value = conTalud.value[conTalud.value.length - 1].x
      if (avance >= NUMPASO) {
        sinCapasTalud.value = sinCapas as boolean
        capasTalud.value = capas as Capa[]
      }
      iniciaDibujo('canvas', dimTalud, WIDTH, HEIGHT)
      gestionaCanvas()
    })
  }
}

function recargaTalud() {
  axios.get('/api/talud/' + props.idTalud).then(function (response: { data: Talud3r }) {
    const { avance, sinCapas, capas } = response.data
    talud.avance = avance
    if (avance >= NUMPASO) {
      sinCapasTalud.value = sinCapas as boolean
      capasTalud.value = capas as Capa[]
    } else {
      sinCapasTalud.value = false
      capasTalud.value = []
    }
    // Reset valores
    finalCapaValido.value = false
    intentoValidarCapa.value = false
    intentoValidarPunto.value = false
    nombreCapa.value = ''
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
  if (errNombreCapa.value) {
    intentoValidarCapa.value = true
  } else {
    axios
      .put(
        '/api/paso' + NUMPASO + '/' + props.idTalud,
        {
          nombre: nombreCapa.value,
          contorno: getContorno()
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

function guardarSinCapas() {
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
      if (capasTalud.value.length >= 1 || sinCapasTalud.value) {
        recargaTalud()
      } else {
        router.push('/paso' + (NUMPASO - 1) + '/' + props.idTalud)
      }
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
    intentoValidarPunto.value = true
  } else {
    const x = Number.parseFloat(nuevoPuntoX.value)
    const y = Number.parseFloat(nuevoPuntoY.value)
    if (validoPuntoCapa(x, y)) nuevoObjeto(x, y)
    intentoValidarPunto.value = false
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
