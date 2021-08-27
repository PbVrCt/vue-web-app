import { TaludBase, Dimensiones, Punto, Material, Centros } from '../types/talud'

export const taludBase: TaludBase = {
  nombre: '',
  codigo: 0,
  avance: 0,
  sinCargas: false
}

export const dimBase: Dimensiones = {
  izquierda: 0,
  derecha: 200,
  abajo: 0,
  arriba: 100,
  gridx: 5,
  gridy: 5,
  intervalosx: 10,
  intervalosy: 10
}

export const puntoBase: Punto = {
  x: 0,
  y: 0
}

export const materialBase: Material = {
  consistencia: 0,
  angulo: 0,
  pseco: 0,
  psaturado: 0,
  cohesion: 0
}

export const centrosBase: Centros = {
  inicioX: 0,
  inicioY: 0,
  desplazaX: 0,
  nradios: 0,
  numeroX: 0,
  numeroY: 0,
  distanciaX: 0,
  distanciaY: 0
}
