<template>
  <div class="container">
    <h1>{{ talud.nombre + ' - ' + TEXTOSPASOS[NUMPASO - 1] }}</h1>
    <pasos-talud :codigo="talud.codigo" :numpaso="NUMPASO" :pasos="pasos(talud)" />
    <h6>
      En FX y FY se pueden utilizar expresiones válidas en Python que contengan o no la variable
      'x'. Por ejemplo: FY( x ) = 5.4 * x + 2.3
    </h6>
    <h6>
      En el caso de fuerzas lineales se puede indicar los valores en los extremos separados por
      punto y coma: FY( x ) = 18.5 ; 34.7
    </h6>
    <p>
      Funciones aceptadas: acos asin atan atan2 ceil cos cosh degrees e exp fabs floor fmod frexp
      hypot ldexp log log10 modf pi pow radians sin sinh sqrt tan tanh
    </p>
    <h3 class="text-danger">{{ error }}</h3>
    <form>
      <div v-for="(carga, ind) in cargasTalud" :key="carga.nombre" class="row mb-4">
        <div class="col-md-6 col-lg-2">
          <label :for="'nombre' + ind" class="form-label fw-bold"
            >Carga {{ ind + 1 }} ({{ COLORESESP[ind] }})</label
          >
          <input
            v-model="carga.nombre"
            :id="'nombre' + ind"
            required
            type="text"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errNombreCr(carga) }"
          />
          <div class="invalid-feedback">Es necesario un nombre</div>
        </div>
        <div class="col-md-6 col-lg-2">
          <label :for="'intervalo' + ind" class="form-label">Intervalo X</label>
          <input
            :id="'intervalo' + ind"
            type="text"
            :value="intervaloCr(carga)"
            readonly
            class="form-control-plaintext fw-bold"
          />
        </div>
        <div class="col-md-6 col-lg-4">
          <label :for="'fx' + ind" class="form-label"><strong>FX</strong>( x ) =</label>
          <input
            v-model="carga.fX"
            :id="'fx' + ind"
            required
            type="text"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errFxCr(carga) }"
          />
          <div class="invalid-feedback">Es necesario una FX</div>
        </div>
        <div class="col-md-6 col-lg-4">
          <label :for="'fy' + ind" class="form-label"><strong>FY</strong>( x ) =</label>
          <input
            v-model="carga.fY"
            :id="'fy' + ind"
            required
            type="text"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errFyCr(carga) }"
          />
          <div class="invalid-feedback">Es necesario una FY</div>
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
import { taludBase } from '../functions/Base'
import { COLORESESP } from '../functions/Colores'
import type { Talud7, Carga } from '../types/talud'
import PasosTalud from '../components/PasosTalud.vue'

const props = defineProps({
  idTalud: Number
})

const router = useRouter()
const { TEXTOSPASOS, pasos } = usePasos()
const NUMPASO = 7

const talud = reactive({ ...taludBase })
const cargasTalud = ref<Carga[]>([])
const error = ref('')
const intentoValidar = ref(false)

const errNombreCr = (c: Carga) => c.nombre.length === 0
const errFxCr = (c: Carga) => c.fX.length === 0
const errFyCr = (c: Carga) => c.fY.length === 0

const intervaloCr = (c: Carga) => {
  let tex = ''
  if (c.xInicial === c.xFinal) {
    tex = '[ ' + c.xInicial + ' ]'
  } else {
    tex = '[ ' + c.xInicial + ' a ' + c.xFinal + ' ]'
  }
  return tex
}

// OBTIENE EL TALUD
function getTalud() {
  if (typeof props.idTalud === 'number' && props.idTalud !== 0) {
    axios.get('/api/talud/' + props.idTalud).then(function (response: { data: Talud7 }) {
      const { nombre, codigo, avance, sinCargas, cargas } = response.data
      Object.assign(talud, { nombre, codigo, avance, sinCargas })
      cargasTalud.value = cargas as Carga[]
      if (avance < NUMPASO) {
        for (const c of cargasTalud.value) {
          c.fX = ''
          c.fY = ''
        }
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
    cargasTalud.value.some((c) => errNombreCr(c)) ||
    cargasTalud.value.some((c) => errFxCr(c)) ||
    cargasTalud.value.some((c) => errFyCr(c))
  ) {
    intentoValidar.value = true
  } else {
    // Para 3 cargas se obtiene indicesCargas === [0,1,2]
    const indicesCargas = [...Array(cargasTalud.value.length).keys()]
    //
    axios
      .put(
        '/api/paso' + NUMPASO + '/' + props.idTalud,
        {
          nombres: indicesCargas.map((i) => cargasTalud.value[i].nombre.trim().toLowerCase()),
          fuerzasX: indicesCargas.map((i) => cargasTalud.value[i].fX),
          fuerzasY: indicesCargas.map((i) => cargasTalud.value[i].fY)
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
