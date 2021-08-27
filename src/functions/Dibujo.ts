import { Ref } from 'vue'
import { fabric } from 'fabric'
import { Dimensiones, Punto, Centros } from '../types/talud'

export function useDibujo() {
  const RULERX = 40 // Pixels en eje X de la regla
  const RULERY = 40 // Pixels en eje Y de la regla
  const LABELX = 16 // Pixels en eje X para ancho de número en la regla
  const LABELY = 16 // Pixels en eje Y para altura de número en la regla

  const TOLERANCIA = 0.001

  let canvas: fabric.Canvas
  let dimen: Dimensiones
  let ANCHO: number // Pixels en eje X del area de dibujo
  let ALTO: number // Pixels en eje Y del area de dibujo
  let contornoCanvas: Punto[] // contiene puntos del contorno en coordenadas de Canvas
  let contornoCustom: Punto[] // contiene puntos del contorno en coordenadas de Proyecto
  let objetosCanvas: any[] // contiene acceso a las lineas dibujadas en el Canvas
  let numeroObjetos: Ref<number> // Número de objetos
  let saveObject: boolean // Indica si se guardan los objetos del Canvas
  let thicknessNew: number // Grosor del trazo de linea
  let colorNew: string // Color de la linea
  let incx: number // Factor de ajuste de precisión en el eje X
  let incy: number // Factor de ajuste de precisión en el eje X
  let puntoActualSpan: HTMLSpanElement // Elemento de la plantilla donde se muestra el punto actual (<span>)
  let puntosHeading: HTMLHeadingElement // Elemento de la plantilla donde se muestran todos los puntos (<h5> o similar)
  let activoEventosDibujo: boolean // Indica si se activaron lo eventos de dibujo
  let activoEventosGeneral: boolean // Indica si se activaron lo eventos de dibujo
  let existeXi: boolean // Indica si se pulsó el primer punto de un intervalo
  let existeXf: boolean // Indica si se pulsó el segundo punto de un intervalo
  let funUp: (options: fabric.IEvent) => void // Función para evento mouse Up
  let funMove: (options: fabric.IEvent) => void // Función para evento mouse Move
  let funOut: (options: fabric.IEvent) => void // Función para evento mouse Out
  let funOver: (event: fabric.IEvent) => void // Función para evento mouse Over

  function iniciaDibujo(c: string, d: Dimensiones, px: number, py: number) {
    canvas = new fabric.Canvas(c, { width: ANCHO, height: ALTO, selection: false })
    dimen = d
    ANCHO = px
    ALTO = py
    incx = dimen.intervalosx / dimen.gridx
    incy = dimen.intervalosy / dimen.gridy
    activoEventosDibujo = false
    activoEventosGeneral = false
    canvas.clear()
  }

  function limpiaDibujo() {
    if (activoEventosDibujo) {
      // ;(canvas as any).__eventListeners['mouse:up'] = []
      // ;(canvas as any).__eventListeners['mouse:move'] = []
      // ;(canvas as any).__eventListeners['mouse:out'] = []
      canvas.off('mouse:up', funUp)
      canvas.off('mouse:move', funMove)
      canvas.off('mouse:out', funOut)
      if (typeof puntosHeading !== 'undefined') puntosHeading.innerHTML = ''
      activoEventosDibujo = false
    }
    if (activoEventosGeneral) {
      // ;(canvas as any).__eventListeners['mouse:over'] = []
      canvas.off('mouse:over', funOver)
      activoEventosGeneral = false
    }
    contornoCustom = []
    contornoCanvas = []
    objetosCanvas = []
    canvas.clear()
  }

  function asignaGrosorYColor(thickNew: number, colNew: string) {
    thicknessNew = thickNew
    colorNew = colNew
  }

  function getContorno() {
    return contornoCustom
  }

  function getPunto(indice: number) {
    return contornoCustom[indice]
  }

  function fueraDeReglaLB(x: number, y: number) {
    return [x >= RULERX, y <= ALTO - RULERY]
  }
  const fueraDeRegla = fueraDeReglaLB

  // Coordenadas de Usuario --> Coordenadas de Canvas
  // REGLA A LA IZQUIERDA Y ABAJO
  function toCanvasLB(x: number, y: number) {
    return [
      ((x - dimen.izquierda) * (ANCHO - RULERX)) / (dimen.derecha - dimen.izquierda) + RULERX,
      ((y - dimen.arriba) * (ALTO - RULERY)) / (dimen.abajo - dimen.arriba)
    ]
  }
  const toCanvas = toCanvasLB

  // Coordenadas de Canvas --> Coordenadas de Usuario
  // REGLA A LA IZQUIERDA Y ABAJO
  function toCustomLB(x: number, y: number) {
    return [
      ((x - RULERX) * (dimen.derecha - dimen.izquierda)) / (ANCHO - RULERX) + dimen.izquierda,
      (y * (dimen.abajo - dimen.arriba)) / (ALTO - RULERY) + dimen.arriba
    ]
  }
  const toCustom = toCustomLB

  function redondea(x: number, y: number) {
    // Primero ajustamos la precisión al numéro de puntos por intervalo
    const rx = Math.round(x * incx) / incx
    const ry = Math.round(y * incy) / incy
    // Luego redondeamos a máximo de 2 decimales para evitar números como 3.0000001
    const rx2 = Math.round(rx * 100) / 100
    const ry2 = Math.round(ry * 100) / 100
    //
    return [rx2, ry2]
  }

  function dibujaPunto(vX: number, vY: number) {
    const [cX, cY] = toCanvas(vX, vY)
    const obj = new fabric.Circle({
      radius: Math.ceil(thicknessNew / 2),
      fill: colorNew,
      selectable: false,
      originX: 'center',
      originY: 'center',
      left: cX,
      top: cY
    })
    canvas.add(obj)
  }

  function dibujaObjeto(n: number, cX: number, cY: number) {
    let obj
    contornoCanvas.push({ x: cX, y: cY })
    if (n === 0) {
      obj = new fabric.Circle({
        radius: Math.ceil(thicknessNew / 2),
        fill: colorNew,
        selectable: false,
        originX: 'center',
        originY: 'center',
        left: contornoCanvas[0].x,
        top: contornoCanvas[0].y
      })
    } else {
      obj = new fabric.Line(
        [
          contornoCanvas[n - 1].x,
          contornoCanvas[n - 1].y,
          contornoCanvas[n].x,
          contornoCanvas[n].y
        ],
        {
          selectable: false,
          stroke: colorNew,
          strokeWidth: thicknessNew,
          originX: 'center',
          originY: 'center'
        }
      )
    }
    if (saveObject) objetosCanvas.push(obj)
    canvas.add(obj)
  }

  function textoPuntos(polig: Punto[]) {
    let tex = ''
    for (const v of polig) {
      tex += '(' + v.x + ',' + v.y + ') '
    }
    return tex
  }

  function textoIntervalo(xi: number, xf: number) {
    let tex = ''
    if (xi === xf) {
      tex = '[ ' + xi + ' ]'
    } else {
      tex = '[ ' + xi + ' a ' + xf + ' ]'
    }
    return tex
  }

  function nuevoObjeto(vX: number, vY: number) {
    contornoCustom.push({ x: vX, y: vY })
    const n = contornoCustom.length - 1
    const [cX, cY] = toCanvas(vX, vY)
    dibujaObjeto(n, cX, cY)
    puntosHeading.innerHTML = textoPuntos(contornoCustom)
    numeroObjetos.value = contornoCustom.length
  }

  function eliminarUltimoObjeto() {
    if (contornoCustom.length > 0) {
      const obj = objetosCanvas.pop()
      canvas.remove(obj)
      contornoCanvas.pop()
      contornoCustom.pop()
      puntosHeading.innerHTML = textoPuntos(contornoCustom)
      numeroObjetos.value = contornoCustom.length
    }
  }

  function eventosDibujo(
    puntoActual: string,
    puntos: string,
    numObjetos: Ref<number>,
    valido: (x: number, y: number) => boolean
  ) {
    if (!activoEventosDibujo) {
      contornoCustom = []
      contornoCanvas = []
      objetosCanvas = []
      puntoActualSpan = document.getElementById(puntoActual) as HTMLSpanElement
      puntosHeading = document.getElementById(puntos) as HTMLHeadingElement
      puntosHeading.innerHTML = ''
      numeroObjetos = numObjetos
      saveObject = true
      // CONFIGURAR FUNCION PARA CUANDO SE PULSA EL RATON EN EL CANVAS
      funUp = function (options) {
        const [inX, inY] = fueraDeRegla(options.pointer?.x as number, options.pointer?.y as number)
        if (inX && inY) {
          const [pX, pY] = toCustom(options.pointer?.x as number, options.pointer?.y as number)
          const [vX, vY] = redondea(pX, pY)
          if (valido(vX, vY)) nuevoObjeto(vX, vY)
        }
      }
      canvas.on('mouse:up', funUp)
      // CONFIGURAR FUNCION PARA CUANDO SE MUEVE EL RATON EN EL CANVAS
      funMove = function (options) {
        const [inX, inY] = fueraDeRegla(options.pointer?.x as number, options.pointer?.y as number)
        if (inX && inY) {
          const [pX, pY] = toCustom(options.pointer?.x as number, options.pointer?.y as number)
          const [vX, vY] = redondea(pX, pY)
          puntoActualSpan.innerHTML = '(' + vX + ',' + vY + ')'
        }
      }
      canvas.on('mouse:move', funMove)
      // CONFIGURAR FUNCION PARA CUANDO SE ABANDONA EL CANVAS
      funOut = function () {
        puntoActualSpan.innerHTML = ''
      }
      canvas.on('mouse:out', funOut)
      //
      activoEventosDibujo = true
    }
  }

  function eventosIntervalo(
    puntoActual: string,
    puntoXi: (xi: string) => void,
    puntoXf: (xf: string) => void,
    valido: (x: number) => boolean
  ) {
    if (!activoEventosDibujo) {
      contornoCustom = []
      contornoCanvas = []
      objetosCanvas = []
      puntoActualSpan = document.getElementById(puntoActual) as HTMLSpanElement
      existeXi = false
      existeXf = false
      saveObject = true
      // CONFIGURAR FUNCION PARA CUANDO SE PULSA EL RATON EN EL CANVAS
      funUp = function (options) {
        const [inX, inY] = fueraDeRegla(options.pointer?.x as number, options.pointer?.y as number)
        if (inX && inY) {
          const [pX, pY] = toCustom(options.pointer?.x as number, options.pointer?.y as number)
          const [vX, _vY] = redondea(pX, pY)
          if (valido(vX)) {
            if (!existeXi) {
              existeXi = true
              puntoXi(vX.toString())
            } else if (!existeXf) {
              existeXf = true
              puntoXf(vX.toString())
            } else {
              existeXi = false
              existeXf = false
              puntoXi('')
              puntoXf('')
            }
          }
        }
      }
      canvas.on('mouse:up', funUp)
      // CONFIGURAR FUNCION PARA CUANDO SE MUEVE EL RATON EN EL CANVAS
      funMove = function (options) {
        const [inX, inY] = fueraDeRegla(options.pointer?.x as number, options.pointer?.y as number)
        if (inX && inY) {
          const [pX, pY] = toCustom(options.pointer?.x as number, options.pointer?.y as number)
          const [vX, vY] = redondea(pX, pY)
          puntoActualSpan.innerHTML = '(' + vX + ',' + vY + ')'
        }
      }
      canvas.on('mouse:move', funMove)
      // CONFIGURAR FUNCION PARA CUANDO SE ABANDONA EL CANVAS
      funOut = function () {
        puntoActualSpan.innerHTML = ''
      }
      canvas.on('mouse:out', funOut)
      //
      activoEventosDibujo = true
    }
  }

  function eventosPunto(
    puntoActual: string,
    puntoX: (x: number) => void,
    puntoY: (y: number) => void,
    valido: (x: number, y: number) => boolean
  ) {
    if (!activoEventosDibujo) {
      contornoCustom = []
      contornoCanvas = []
      objetosCanvas = []
      puntoActualSpan = document.getElementById(puntoActual) as HTMLSpanElement
      saveObject = true
      // CONFIGURAR FUNCION PARA CUANDO SE PULSA EL RATON EN EL CANVAS
      funUp = function (options) {
        const [inX, inY] = fueraDeRegla(options.pointer?.x as number, options.pointer?.y as number)
        if (inX && inY) {
          const [pX, pY] = toCustom(options.pointer?.x as number, options.pointer?.y as number)
          const [vX, vY] = redondea(pX, pY)
          if (valido(vX, vY)) {
            puntoX(vX)
            puntoY(vY)
          }
        }
      }
      canvas.on('mouse:up', funUp)
      // CONFIGURAR FUNCION PARA CUANDO SE MUEVE EL RATON EN EL CANVAS
      funMove = function (options) {
        const [inX, inY] = fueraDeRegla(options.pointer?.x as number, options.pointer?.y as number)
        if (inX && inY) {
          const [pX, pY] = toCustom(options.pointer?.x as number, options.pointer?.y as number)
          const [vX, vY] = redondea(pX, pY)
          puntoActualSpan.innerHTML = '(' + vX + ',' + vY + ')'
        }
      }
      canvas.on('mouse:move', funMove)
      // CONFIGURAR FUNCION PARA CUANDO SE ABANDONA EL CANVAS
      funOut = function () {
        puntoActualSpan.innerHTML = ''
      }
      canvas.on('mouse:out', funOut)
      //
      activoEventosDibujo = true
    }
  }

  function eventosGeneral() {
    if (!activoEventosGeneral) {
      // CONFIGURAR FUNCION PARA CUANDO SE APROXIMA A UN OBJETO
      funOver = function (event) {
        if (event.target != null) event.target.hoverCursor = canvas.defaultCursor
      }
      canvas.on('mouse:over', funOver)
      activoEventosGeneral = false
    }
  }

  function dibujaContorno(cnt: Punto[]) {
    contornoCustom = cnt
    contornoCanvas = []
    objetosCanvas = []
    saveObject = false
    const np = contornoCustom.length
    for (let n = 0; n < np; ++n) {
      const [cX, cY] = toCanvas(contornoCustom[n].x, contornoCustom[n].y)
      dibujaObjeto(n, cX, cY)
    }
  }

  function dibujaCentros(c: Centros) {
    let x
    let y
    for (let ny = 0; ny < c.numeroY; ++ny) {
      y = c.inicioY + ny * c.distanciaY
      for (let nx = 0; nx < c.numeroX; ++nx) {
        x = c.inicioX + nx * c.distanciaX + ny * c.desplazaX
        dibujaPunto(x, y)
      }
    }
  }

  function puntosPoligono(
    numLados: number,
    radio: number,
    centroX: number,
    centroY: number,
    fraccionAnguloGiro: number,
    cerrado: boolean
  ) {
    const angulo = (2 * Math.PI) / numLados
    const frac = angulo * fraccionAnguloGiro
    const puntos: Punto[] = []
    for (let i = 0; i < numLados; i++) {
      puntos.push({
        x: centroX + radio * Math.sin(i * angulo + frac),
        y: centroY + radio * Math.cos(i * angulo + frac)
      })
    }
    if (cerrado) puntos.push(puntos[0])
    return puntos
  }

  function dibujaRadios(vX: number, vY: number, rMin: number, rMax: number, nRad: number) {
    const ladosPolig = 128 // Aproximación a circulo
    let p: Punto[]
    let x1, y1, x2, y2: number
    let obj
    let inc = 9999
    if (nRad === 1) rMax = rMin
    else inc = (rMax - rMin) / (nRad - 1)
    //
    for (let r = rMin; r <= rMax + TOLERANCIA; r += inc) {
      p = puntosPoligono(ladosPolig, r, vX, vY, 0, true)
      // Al ser poligono cerrado: Numero puntos = ladosPolig + 1
      for (let i = 0; i < ladosPolig; ++i) {
        if (
          p[i].x >= dimen.izquierda &&
          p[i].x <= dimen.derecha &&
          p[i].y >= dimen.abajo &&
          p[i].y <= dimen.arriba &&
          p[i + 1].x >= dimen.izquierda &&
          p[i + 1].x <= dimen.derecha &&
          p[i + 1].y >= dimen.abajo &&
          p[i + 1].y <= dimen.arriba
        ) {
          ;[x1, y1] = toCanvas(p[i].x, p[i].y)
          ;[x2, y2] = toCanvas(p[i + 1].x, p[i + 1].y)
          obj = new fabric.Line([x1, y1, x2, y2], {
            selectable: false,
            stroke: colorNew,
            strokeWidth: thicknessNew,
            originX: 'center',
            originY: 'center'
          })
          canvas.add(obj)
        }
      }
    }
  }

  function dibujaRadio(vX: number, vY: number, r: number) {
    const ladosPolig = 128 // Aproximación a circulo
    let x1, y1, x2, y2: number
    let obj
    //
    const p = puntosPoligono(ladosPolig, r, vX, vY, 0, true)
    // Al ser poligono cerrado: Numero puntos = ladosPolig + 1
    for (let i = 0; i < ladosPolig; ++i) {
      if (
        p[i].x >= dimen.izquierda &&
        p[i].x <= dimen.derecha &&
        p[i].y >= dimen.abajo &&
        p[i].y <= dimen.arriba &&
        p[i + 1].x >= dimen.izquierda &&
        p[i + 1].x <= dimen.derecha &&
        p[i + 1].y >= dimen.abajo &&
        p[i + 1].y <= dimen.arriba
      ) {
        ;[x1, y1] = toCanvas(p[i].x, p[i].y)
        ;[x2, y2] = toCanvas(p[i + 1].x, p[i + 1].y)
        obj = new fabric.Line([x1, y1, x2, y2], {
          selectable: false,
          stroke: colorNew,
          strokeWidth: thicknessNew,
          originX: 'center',
          originY: 'center'
        })
        canvas.add(obj)
      }
    }
  }

  function etiq(n: number) {
    return (Math.round(n * 100) / 100).toString()
  }

  function dibujaReglaLB() {
    let x, y
    // IZQUIERDA
    canvas.add(
      new fabric.Rect({
        left: 0,
        top: 0,
        fill: '#DDD',
        selectable: false,
        width: RULERX,
        height: ALTO
      })
    )
    // ABAJO
    canvas.add(
      new fabric.Rect({
        left: 0,
        top: ALTO - RULERY,
        fill: '#DDD',
        selectable: false,
        width: ANCHO,
        height: RULERY
      })
    )
    // IZQUIERDA
    for (let i = dimen.abajo; i < dimen.arriba; i += dimen.gridy) {
      ;[x, y] = toCanvasLB(0, i)
      canvas.add(
        new fabric.Line([RULERX - 5, y, ANCHO, y], {
          selectable: false,
          stroke: 'black',
          strokeWidth: 0.5
        })
      )
      if (y > LABELY) {
        // Si no cabe se omite la penultima etiqueta de grid
        canvas.add(
          new fabric.Text(etiq(i), {
            left: 5,
            top: y - 6,
            fontSize: 12,
            selectable: false
          })
        )
      }
    }
    // el ultimo por arriba
    ;[x, y] = toCanvasLB(0, dimen.arriba)
    if (y < LABELY) {
      canvas.add(
        new fabric.Text(etiq(dimen.arriba), {
          left: 5,
          top: 0,
          fontSize: 12,
          selectable: false
        })
      ) // El extremo superior
    }
    // ABAJO
    for (let i = dimen.izquierda; i < dimen.derecha; i += dimen.gridx) {
      ;[x, y] = toCanvasLB(i, 0)
      canvas.add(
        new fabric.Line([x, 0, x, ALTO - RULERY + 5], {
          selectable: false,
          stroke: 'black',
          strokeWidth: 0.5
        })
      )
      if (x < ANCHO - LABELX) {
        // Si no cabe se omite la penultima etiqueta de grid
        canvas.add(
          new fabric.Text(etiq(i), {
            left: x - 6,
            top: ALTO - 5,
            fontSize: 12,
            angle: -90,
            selectable: false
          })
        )
      }
    }
    // el ultimo por la derecha
    ;[x, y] = toCanvasLB(dimen.derecha, 0)
    if (x > ANCHO - LABELX) {
      canvas.add(
        new fabric.Text(etiq(dimen.derecha), {
          left: ANCHO - 12,
          top: ALTO - 5,
          fontSize: 12,
          angle: -90,
          selectable: false
        })
      ) // El extremo derecho
    }
  }

  const dibujaRegla = dibujaReglaLB

  return {
    iniciaDibujo,
    asignaGrosorYColor,
    getContorno,
    getPunto,
    limpiaDibujo,
    textoPuntos,
    textoIntervalo,
    nuevoObjeto,
    eliminarUltimoObjeto,
    eventosDibujo,
    eventosIntervalo,
    eventosPunto,
    eventosGeneral,
    dibujaContorno,
    dibujaPunto,
    dibujaCentros,
    dibujaRadios,
    dibujaRadio,
    dibujaRegla
  }
}
