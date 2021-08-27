import { TaludBase } from '../types/talud'

export function usePasos() {
  // Obtener textos de los pasos
  const TEXTOSPASOS = [
    'Dimensiones',
    'Contorno',
    'Capas',
    'Materiales',
    'N. Freático',
    'Pos. Cargas',
    'Cargas',
    'Centros Cir.',
    'Radios Cir.',
    'Método',
    'Análisis'
  ]

  const PASOOPCIONAL = 6 // EMPEZANDO POR CERO; RESTADO 1
  const MODIFICABLES = [0, 3, 4, 6, 8, 9] // EMPEZANDO POR CERO; RESTADO 1

  // CALCULA LOS PASOS CON DATOS DE UN TALUD EMPEZANDO POR CERO
  function pasos(talud: TaludBase) {
    let nPasos = talud.avance
    if (nPasos === PASOOPCIONAL && talud.sinCargas) {
      nPasos = nPasos + 2
    } else if (nPasos + 1 < TEXTOSPASOS.length) {
      nPasos = nPasos + 1
    }
    const ps: number[] = []
    for (let i = 0; i < nPasos; ++i) {
      if (i !== PASOOPCIONAL || !talud.sinCargas) {
        ps.push(i)
      }
    }
    return ps
  }

  // ESTILO DIFERENTE SI SE PUEDEN MODIFICAR LOS DATOS EN EL PASO
  function estiloPaso(p: number, actual: number) {
    let estilo = ''
    if (p === actual) {
      estilo = 'btn-outline-secondary disabled'
    } else if (MODIFICABLES.includes(p)) {
      estilo = 'btn-success'
    } else {
      estilo = 'btn-secondary'
    }
    return estilo
  }

  return { TEXTOSPASOS, pasos, estiloPaso }
}
