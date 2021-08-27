<template>
  <div class="container">
    <h1>{{ talud.nombre + ' - ' + TEXTOSPASOS[NUMPASO - 1] }}</h1>
    <pasos-talud :codigo="talud.codigo" :numpaso="NUMPASO" :pasos="pasos(talud)" />
    <h3 class="text-danger">{{ error }}</h3>
    <form>
      <div class="row mb-3">
        <div class="col-md-9">
          <label for="nombre" class="form-label">Nombre del talud</label>
          <input
            v-model="nombreTalud"
            id="nombre"
            required
            type="text"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errNombre }"
          />
          <div class="invalid-feedback">Es necesario un nombre</div>
        </div>
      </div>
      <div class="row mb-3">
        <div class="col-md-4">
          <label for="izquierda" class="form-label">Izquierda (en metros)</label>
          <input
            v-model.number="dimTalud.izquierda"
            id="izquierda"
            required
            type="number"
            min="-10000"
            step="1"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errIzquierda }"
          />
          <div class="invalid-feedback">Es necesario un número entero</div>
        </div>
        <div class="col-md-4 offset-md-1">
          <label for="derecha" class="form-label">Derecha (en metros)</label>
          <input
            v-model.number="dimTalud.derecha"
            id="derecha"
            required
            type="number"
            min="-10000"
            step="1"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errDerecha }"
          />
          <div class="invalid-feedback">
            Es necesario un número entero mayor que para 'izquierda'
          </div>
        </div>
      </div>
      <div class="row mb-3">
        <div class="col-md-4">
          <label for="abajo" class="form-label">Abajo (en metros)</label>
          <input
            v-model.number="dimTalud.abajo"
            id="abajo"
            required
            type="number"
            min="-10000"
            step="1"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errAbajo }"
          />
          <div class="invalid-feedback">Es necesario un número entero</div>
        </div>
        <div class="col-md-4 offset-md-1">
          <label for="arriba" class="form-label">Arriba (en metros)</label>
          <input
            v-model.number="dimTalud.arriba"
            id="arriba"
            required
            type="number"
            min="-10000"
            step="1"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errArriba }"
          />
          <div class="invalid-feedback">Es necesario un número entero mayor que para 'abajo'</div>
        </div>
      </div>
      <div class="row mb-3">
        <div class="col-md-4">
          <label for="gridx" class="form-label">Grid X (en metros)</label>
          <input
            v-model.number="dimTalud.gridx"
            id="gridx"
            required
            type="number"
            min="1"
            step="1"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errGridx }"
          />
          <div class="invalid-feedback">
            Grid X debe ser entero positivo entre {{ gridxmin }} y
            {{ gridxmax }}
          </div>
        </div>
        <div class="col-md-4 offset-md-1">
          <label for="gridy" class="form-label">Grid Y (en metros)</label>
          <input
            v-model.number="dimTalud.gridy"
            id="gridy"
            required
            type="number"
            min="1"
            step="1"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errGridy }"
          />
          <div class="invalid-feedback">
            Grid Y debe ser entero positivo entre {{ gridymin }} y
            {{ gridymax }}
          </div>
        </div>
      </div>
      <div class="row mb-3">
        <div class="col-md-4">
          <label for="intervalosx" class="form-label">Puntos X entre cada Grid X</label>
          <input
            v-model.number="dimTalud.intervalosx"
            id="intervalosx"
            required
            type="number"
            min="1"
            step="1"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errIntervalosx }"
          />
          <div class="invalid-feedback">Es necesario un número entero positivo mayor que cero</div>
        </div>
        <div class="col-md-4 offset-md-1">
          <label for="intervalosy" class="form-label">Puntos Y entre cada Grid Y</label>
          <input
            v-model.number="dimTalud.intervalosy"
            id="intervalosy"
            required
            type="number"
            min="1"
            step="1"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errIntervalosy }"
          />
          <div class="invalid-feedback">Es necesario un número entero positivo mayor que cero</div>
        </div>
      </div>
    </form>
    <div class="my-3">
      <router-link to="/" class="btn btn-secondary btn-sm">Inicio</router-link>
      <button
        v-if="talud.avance === NUMPASO"
        @click="eliminar"
        type="button"
        class="btn btn-danger btn-sm ms-3"
      >
        Eliminar talud
      </button>
      <button @click="deshacer" type="button" class="btn btn-warning btn-sm ms-3">Deshacer</button>
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
import { taludBase, dimBase } from '../functions/Base'
import type { Talud1 } from '../types/talud'
import PasosTalud from '../components/PasosTalud.vue'

const props = defineProps({
  idTalud: Number
})

const router = useRouter()
const { TEXTOSPASOS, pasos } = usePasos()
const NUMPASO = 1
const MINDIVX = 20 // Mínimo de rayas grid en eje X
const MAXDIVX = 50 // Máximo de rayas grid en eje X
const MINDIVY = 14 // Mínimo de rayas grid en eje Y
const MAXDIVY = 35 // Máximo de rayas grid en eje Y

const talud = reactive({ ...taludBase })
const nombreTalud = ref('')
const dimTalud = reactive({ ...dimBase })
const error = ref('') // Error
const intentoValidar = ref(false) // Intento Validar

const gridxmin = computed(() => Math.ceil((dimTalud.derecha - dimTalud.izquierda) / MAXDIVX))
const gridxmax = computed(() => Math.floor((dimTalud.derecha - dimTalud.izquierda) / MINDIVX))
const gridymin = computed(() => Math.ceil((dimTalud.arriba - dimTalud.abajo) / MAXDIVY))
const gridymax = computed(() => Math.ceil((dimTalud.arriba - dimTalud.abajo) / MINDIVY))
const errNombre = computed(() => nombreTalud.value.length === 0)
const errIzquierda = computed(
  () => typeof dimTalud.izquierda !== 'number' || dimTalud.izquierda % 1 !== 0
)
const errDerecha = computed(
  () =>
    typeof dimTalud.derecha !== 'number' ||
    dimTalud.derecha % 1 !== 0 ||
    dimTalud.derecha <= dimTalud.izquierda
)
const errAbajo = computed(() => typeof dimTalud.abajo !== 'number' || dimTalud.abajo % 1 !== 0)
const errArriba = computed(
  () =>
    typeof dimTalud.arriba !== 'number' ||
    dimTalud.arriba % 1 !== 0 ||
    dimTalud.arriba <= dimTalud.abajo
)
const errGridx = computed(
  () =>
    typeof dimTalud.gridx !== 'number' ||
    dimTalud.gridx % 1 !== 0 ||
    dimTalud.gridx < gridxmin.value ||
    dimTalud.gridx > gridxmax.value
)
const errGridy = computed(
  () =>
    typeof dimTalud.gridy !== 'number' ||
    dimTalud.gridy % 1 !== 0 ||
    dimTalud.gridy < gridymin.value ||
    dimTalud.gridy > gridymax.value
)
const errIntervalosx = computed(
  () =>
    typeof dimTalud.intervalosx !== 'number' ||
    dimTalud.intervalosx % 1 !== 0 ||
    dimTalud.intervalosx < 1
)
const errIntervalosy = computed(
  () =>
    typeof dimTalud.intervalosy !== 'number' ||
    dimTalud.intervalosy % 1 !== 0 ||
    dimTalud.intervalosy < 1
)

// OBTIENE EL TALUD
function getTalud() {
  if (typeof props.idTalud === 'number' && props.idTalud !== 0) {
    axios.get('/api/talud/' + props.idTalud).then(function (response: { data: Talud1 }) {
      const { nombre, codigo, avance, sinCargas, dimensiones } = response.data
      Object.assign(talud, { nombre, codigo, avance, sinCargas })
      nombreTalud.value = nombre
      if (avance >= NUMPASO) {
        Object.assign(dimTalud, dimensiones)
      } else {
        Object.assign(dimTalud, { ...dimBase })
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
  if (
    errNombre.value ||
    errIzquierda.value ||
    errDerecha.value ||
    errAbajo.value ||
    errArriba.value ||
    errGridx.value ||
    errGridy.value ||
    errIntervalosx.value ||
    errIntervalosy.value
  ) {
    intentoValidar.value = true
  } else {
    axios
      .put(
        '/api/paso' + NUMPASO + '/' + props.idTalud,
        {
          nombre: nombreTalud.value,
          dimensiones: dimTalud
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
      router.push('/')
    })
    .catch(function (errorAPI) {
      error.value = errorAPI.response.data.message
    })
}

// SE EJECUTA AL MONTAR LA VISTA
onMounted(getTalud)
</script>
