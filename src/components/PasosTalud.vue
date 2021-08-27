<template>
  <div class="my-3">
    <router-link
      v-for="paso in pasos"
      :key="paso"
      :to="{ path: '/paso' + (paso + 1) + '/' + codigo }"
      class="btn btn-sm me-2 mb-2"
      :class="estiloPaso(paso, numpaso - 1)"
      >{{ TEXTOSPASOS[paso] }}</router-link
    >
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue'
import { usePasos } from '../functions/Pasos'

export default defineComponent({
  name: 'PasosTalud',
  props: {
    codigo: {
      type: Number as PropType<number>,
      required: true
    },
    pasos: {
      type: Array as PropType<number[]>,
      required: true
    },
    numpaso: {
      type: Number as PropType<number>,
      required: true
    }
  },
  setup() {
    const { TEXTOSPASOS, estiloPaso } = usePasos()
    return { TEXTOSPASOS, estiloPaso }
  }
})
</script>
