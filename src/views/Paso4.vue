<template>
  <div class="container">
    <h1>{{ talud.nombre + ' - ' + TEXTOSPASOS[NUMPASO - 1] }}</h1>
    <pasos-talud :codigo="talud.codigo" :numpaso="NUMPASO" :pasos="pasos(talud)" />
    <h3 class="text-danger">{{ error }}</h3>
    <form>
      <div class="row mb-4">
        <div class="col-sm-6 col-md-4 col-lg-2">
          <label for="nombreEx" class="form-label fw-bold">Material Exterior</label>
          <input
            v-model="nombreMaterialTalud"
            id="nombreEx"
            required
            type="text"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errNombreEx }"
          />
          <div class="invalid-feedback">Es necesario un material</div>
        </div>
        <div class="col-sm-6 col-md-4 col-lg-2">
          <label for="consistenciaEx" class="form-label">Consistencia</label>
          <input
            v-model.number="materialTalud.consistencia"
            id="consistenciaEx"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errConsistenciaEx }"
          />
          <div class="invalid-feedback">Es necesario un número</div>
        </div>
        <div class="col-sm-6 col-md-4 col-lg-2">
          <label for="anguloEx" class="form-label">Angulo Fricción I.</label>
          <input
            v-model.number="materialTalud.angulo"
            id="anguloEx"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errAnguloEx }"
          />
          <div class="invalid-feedback">Es necesario un número</div>
        </div>
        <div class="col-sm-6 col-md-4 col-lg-2">
          <label for="psecoEx" class="form-label">Peso E. Seco</label>
          <input
            v-model.number="materialTalud.pseco"
            id="psecoEx"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errPsecoEx }"
          />
          <div class="invalid-feedback">Es necesario un número</div>
        </div>
        <div class="col-sm-6 col-md-4 col-lg-2">
          <label for="psaturadoEx" class="form-label">Peso E. Saturado</label>
          <input
            v-model.number="materialTalud.psaturado"
            id="psaturadoEx"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errPsaturadoEx }"
          />
          <div class="invalid-feedback">Es necesario un número</div>
        </div>
        <div class="col-sm-6 col-md-4 col-lg-2">
          <label for="cohesionEx" class="form-label">Cohesión</label>
          <input
            v-model.number="materialTalud.cohesion"
            id="cohesionEx"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errCohesionEx }"
          />
          <div class="invalid-feedback">Es necesario un número</div>
        </div>
      </div>
      <div v-for="(capa, ind) in capasTalud" :key="capa.nombre" class="row mb-4">
        <div class="col-sm-6 col-md-4 col-lg-2">
          <label :for="'nombre' + ind" class="form-label fw-bold"
            >Mat. {{ ind + 1 }} ({{ COLORESESP[ind] }})</label
          >
          <input
            v-model="capa.nombre"
            :id="'nombre' + ind"
            required
            type="text"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errNombreCp(capa) }"
          />
          <div class="invalid-feedback">Es necesario un material</div>
        </div>
        <div class="col-sm-6 col-md-4 col-lg-2">
          <label :for="'consistencia' + ind" class="form-label">Consistencia</label>
          <input
            v-model.number="capa.material.consistencia"
            :id="'consistencia' + ind"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errConsistenciaCp(capa) }"
          />
          <div class="invalid-feedback">Es necesario un número</div>
        </div>
        <div class="col-sm-6 col-md-4 col-lg-2">
          <label :for="'angulo' + ind" class="form-label">Angulo Fricción I.</label>
          <input
            v-model.number="capa.material.angulo"
            :id="'angulo' + ind"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errAnguloCp(capa) }"
          />
          <div class="invalid-feedback">Es necesario un número</div>
        </div>
        <div class="col-sm-6 col-md-4 col-lg-2">
          <label :for="'pseco' + ind" class="form-label">Peso E. Seco</label>
          <input
            v-model.number="capa.material.pseco"
            :id="'pseco' + ind"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errPsecoCp(capa) }"
          />
          <div class="invalid-feedback">Es necesario un número</div>
        </div>
        <div class="col-sm-6 col-md-4 col-lg-2">
          <label :for="'psaturado' + ind" class="form-label">Peso E. Saturado</label>
          <input
            v-model.number="capa.material.psaturado"
            :id="'psaturado' + ind"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errPsaturadoCp(capa) }"
          />
          <div class="invalid-feedback">Es necesario un número</div>
        </div>
        <div class="col-sm-6 col-md-4 col-lg-2">
          <label :for="'cohesion' + ind" class="form-label">Cohesión</label>
          <input
            v-model.number="capa.material.cohesion"
            :id="'cohesion' + ind"
            required
            type="number"
            class="form-control"
            :class="{ 'is-invalid': intentoValidar && errCohesionCp(capa) }"
          />
          <div class="invalid-feedback">Es necesario un número</div>
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
import { taludBase, materialBase } from '../functions/Base'
import { COLORESESP } from '../functions/Colores'
import type { Talud4, Capa, Material } from '../types/talud'
import PasosTalud from '../components/PasosTalud.vue'

const props = defineProps({
  idTalud: Number
})

const router = useRouter()
const { TEXTOSPASOS, pasos } = usePasos()
const NUMPASO = 4

const talud = reactive({ ...taludBase })
const capasTalud = ref<Capa[]>([])
const materialTalud = reactive({ ...materialBase })
const error = ref('')
const intentoValidar = ref(false)

const nombreMaterialTalud = ref('')

const errNombreEx = computed(() => nombreMaterialTalud.value.length === 0)
const errConsistenciaEx = computed(() => typeof materialTalud.consistencia !== 'number')
const errAnguloEx = computed(() => typeof materialTalud.angulo !== 'number')
const errPsecoEx = computed(() => typeof materialTalud.pseco !== 'number')
const errPsaturadoEx = computed(() => typeof materialTalud.psaturado !== 'number')
const errCohesionEx = computed(() => typeof materialTalud.cohesion !== 'number')

const errNombreCp = (c: Capa) => c.nombre.length === 0
const errConsistenciaCp = (c: Capa) => typeof c.material.consistencia !== 'number'
const errAnguloCp = (c: Capa) => typeof c.material.angulo !== 'number'
const errPsecoCp = (c: Capa) => typeof c.material.pseco !== 'number'
const errPsaturadoCp = (c: Capa) => typeof c.material.psaturado !== 'number'
const errCohesionCp = (c: Capa) => typeof c.material.cohesion !== 'number'

// OBTIENE EL TALUD
function getTalud() {
  if (typeof props.idTalud === 'number' && props.idTalud !== 0) {
    axios.get('/api/talud/' + props.idTalud).then(function (response: { data: Talud4 }) {
      const { nombre, codigo, avance, sinCargas, nombreMaterial, capas, material } = response.data
      Object.assign(talud, { nombre, codigo, avance, sinCargas })
      capasTalud.value = capas as Capa[]
      nombreMaterialTalud.value = nombreMaterial
      if (avance >= NUMPASO) {
        Object.assign(materialTalud, material)
      } else {
        for (const c of capasTalud.value) {
          c.material = { ...materialBase }
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
    errNombreEx.value ||
    errConsistenciaEx.value ||
    errAnguloEx.value ||
    errPsecoEx.value ||
    errPsaturadoEx.value ||
    errCohesionEx.value ||
    capasTalud.value.some((c) => errNombreCp(c)) ||
    capasTalud.value.some((c) => errConsistenciaCp(c)) ||
    capasTalud.value.some((c) => errAnguloCp(c)) ||
    capasTalud.value.some((c) => errPsecoCp(c)) ||
    capasTalud.value.some((c) => errPsaturadoCp(c)) ||
    capasTalud.value.some((c) => errCohesionCp(c))
  ) {
    intentoValidar.value = true
  } else {
    // Para 3 capas se obtiene indicesCapas === [0,1,2]
    const indicesCapas = [...Array(capasTalud.value.length).keys()]
    //
    axios
      .put(
        '/api/paso' + NUMPASO + '/' + props.idTalud,
        {
          nombreMaterial: nombreMaterialTalud.value.trim().toLowerCase(),
          material: materialTalud,
          nombresMaterialesCapas: indicesCapas.map((i) => capasTalud.value[i].nombre),
          materialesCapas: indicesCapas.map((i) => capasTalud.value[i].material)
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
