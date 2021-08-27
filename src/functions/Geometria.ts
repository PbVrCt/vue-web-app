import { Punto, Segmento } from '../types/talud'

export function useGeometria() {
  const TOLERANCIAY = 0.001 // Tolerancia para considerar que dos Y son la misma

  // Para un contorno dado busca segmentos con los 2 puntos más cercanos a una X dada
  function xProximas(polig: Punto[], x: number) {
    const n = polig.length - 1
    const segmentos: Segmento[] = []
    for (let i = 0; i < n; ++i) {
      if (x >= polig[i].x && x <= polig[i + 1].x) {
        segmentos.push({ x1: polig[i].x, y1: polig[i].y, x2: polig[i + 1].x, y2: polig[i + 1].y })
      }
    }
    return segmentos
  }

  // Si punto (x,y) está en el segmento 's'
  function enSegmento(x: number, y: number, s: Segmento) {
    let ok = (x === s.x1 && y === s.y1) || (x === s.x2 && y === s.y2)
    if (!ok) {
      const m = (s.y2 - s.y1) / (s.x2 - s.x1)
      const yr = s.y1 + m * (x - s.x1)
      ok = Math.abs(y - yr) < TOLERANCIAY
    }
    return ok
  }

  // Comprueba que 'enSegmento' devuelve true para el segmento correspondiente de 'polig'
  function enSegmentoPolig(polig: Punto[], x: number, y: number) {
    // Busca intervalos que contienen X
    const segmentos = xProximas(polig, x)
    const n = segmentos.length
    if (n === 0) return false
    let ok = false
    let i = 0
    while (!ok && i < n) {
      // Comprueba que la Y es igual
      ok = enSegmento(x, y, segmentos[i])
      if (!ok) ++i
    }
    return ok
  }

  // Si punto (x,y) está por debajo o en el segmento 's'
  function porDebajo(x: number, y: number, s: Segmento) {
    const m = (s.y2 - s.y1) / (s.x2 - s.x1)
    const yr = s.y1 + m * (x - s.x1)
    return y - yr < TOLERANCIAY
  }

  // Si punto (x,y) está por encima o en el segmento 's'
  function porEncima(x: number, y: number, s: Segmento) {
    const m = (s.y2 - s.y1) / (s.x2 - s.x1)
    const yr = s.y1 + m * (x - s.x1)
    return yr - y < TOLERANCIAY
  }

  // Comprueba que 'porDebajo' devuelve true para el segmento correspondiente de 'polig'
  function porDebajoPolig(polig: Punto[], x: number, y: number, resultadoFueraPoligono: boolean) {
    // Busca intervalos que contienen X
    const segmentos = xProximas(polig, x)
    const n = segmentos.length
    if (n === 0) return resultadoFueraPoligono
    let ok = true
    let i = 0
    while (ok && i < n) {
      // Comprueba que la Y es igual
      ok = porDebajo(x, y, segmentos[i])
      ++i
    }
    return ok
  }

  // Comprueba que 'porEncima' devuelve true para el segmento correspondiente de 'polig'
  function porEncimaPolig(polig: Punto[], x: number, y: number, resultadoFueraPoligono: boolean) {
    // Busca intervalos que contienen X
    const segmentos = xProximas(polig, x)
    const n = segmentos.length
    if (n === 0) return resultadoFueraPoligono
    let ok = true
    let i = 0
    while (ok && i < n) {
      // Comprueba que la Y es igual
      ok = porEncima(x, y, segmentos[i])
      ++i
    }
    return ok
  }

  // Calcula Y para el punto cuyo X está en la recta (x1,y1) a (x2,y2)
  function calculaYenRecta(x: number, x1: number, y1: number, x2: number, y2: number) {
    const m = (y2 - y1) / (x2 - x1)
    return y1 + m * (x - x1)
  }

  // Dado el contorno externo y las X de inicio y final de la carga, obtiene el contorno de la carga
  function recortaPoligono(poligEntero: Punto[], xi: number, xf: number) {
    const poligRecortado = []
    // Primer punto de la carga. Puede no coincidir con un punto del contorno externo
    let i = 1
    while (poligEntero[i].x < xi) ++i
    let y = calculaYenRecta(
      xi,
      poligEntero[i - 1].x,
      poligEntero[i - 1].y,
      poligEntero[i].x,
      poligEntero[i].y
    )
    poligRecortado.push({ x: xi, y: y })
    // Puntos de la carga coincidentes con puntos del contorno externo
    while (poligEntero[i].x < xf) {
      poligRecortado.push({ x: poligEntero[i].x, y: poligEntero[i].y })
      ++i
    }
    // Ultimo punto de la carga. Puede no coincidir con un punto del contorno externo
    y = calculaYenRecta(
      xf,
      poligEntero[i - 1].x,
      poligEntero[i - 1].y,
      poligEntero[i].x,
      poligEntero[i].y
    )
    poligRecortado.push({ x: xf, y: y })
    //
    return poligRecortado
  }

  // Dado el contorno externo y las X de inicio y final de la carga, obtiene el contorno de la carga
  function calculaYenPoligono(polig: Punto[], x: number) {
    let i = 1
    while (polig[i].x < x) ++i
    const y = calculaYenRecta(x, polig[i - 1].x, polig[i - 1].y, polig[i].x, polig[i].y)
    //
    return y
  }

  // Devuelve true si intersecciona el segmento r con el segmento s
  // Código obtenido en https://stackoverflow.com/questions/9043805/test-if-two-lines-intersect-javascript-function
  function intersecciona(r: Segmento, s: Segmento) {
    const det = (r.x2 - r.x1) * (s.y2 - s.y1) - (s.x2 - s.x1) * (r.y2 - r.y1)
    if (det === 0) {
      return false
    } else {
      const lambda = ((s.y2 - s.y1) * (s.x2 - r.x1) + (s.x1 - s.x2) * (s.y2 - r.y1)) / det
      const gamma = ((r.y1 - r.y2) * (s.x2 - r.x1) + (r.x2 - r.x1) * (s.y2 - r.y1)) / det
      return lambda > 0 && lambda < 1 && gamma > 0 && gamma < 1
    }
  }

  // Comprueba que 'intersecciona' devuelve true para todos los segmentos de 'polig'
  function interseccionaPolig(x1: number, y1: number, x2: number, y2: number, polig: Punto[]) {
    const n = polig.length - 1
    let i = 0
    let ok = false
    while (!ok && i < n) {
      ok = intersecciona(
        {
          x1,
          y1,
          x2,
          y2
        },
        {
          x1: polig[i].x,
          y1: polig[i].y,
          x2: polig[i + 1].x,
          y2: polig[i + 1].y
        }
      )
      if (!ok) ++i
    }
    return ok
  }

  function distanciaPuntosCuadrado(v: Punto, w: Punto) {
    return (v.x - w.x) * (v.x - w.x) + (v.y - w.y) * (v.y - w.y)
  }

  function distanciaPuntos(v: Punto, w: Punto) {
    return Math.sqrt(distanciaPuntosCuadrado(v, w))
  }

  function distanciaPuntoSegmentoCuadrado(p: Punto, v: Punto, w: Punto) {
    const l2 = distanciaPuntosCuadrado(v, w)
    if (l2 === 0) return distanciaPuntosCuadrado(p, v)
    const t = ((p.x - v.x) * (w.x - v.x) + (p.y - v.y) * (w.y - v.y)) / l2
    if (t < 0) return distanciaPuntosCuadrado(p, v)
    if (t > 1) return distanciaPuntosCuadrado(p, w)
    return distanciaPuntosCuadrado(p, { x: v.x + t * (w.x - v.x), y: v.y + t * (w.y - v.y) })
  }

  function distanciaMinima(p: Punto, s: Segmento) {
    return Math.sqrt(distanciaPuntoSegmentoCuadrado(p, { x: s.x1, y: s.y1 }, { x: s.x2, y: s.y2 }))
  }

  function distanciaMaxima(p: Punto, s: Segmento) {
    return Math.sqrt(
      Math.max(
        distanciaPuntosCuadrado(p, { x: s.x1, y: s.y1 }),
        distanciaPuntosCuadrado(p, { x: s.x2, y: s.y2 })
      )
    )
  }

  return {
    enSegmentoPolig,
    porDebajoPolig,
    porEncimaPolig,
    interseccionaPolig,
    recortaPoligono,
    calculaYenPoligono,
    distanciaPuntos,
    distanciaMinima,
    distanciaMaxima
  }
}
