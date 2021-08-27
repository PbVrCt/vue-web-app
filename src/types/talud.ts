export type Dimensiones = {
  izquierda: number
  derecha: number
  abajo: number
  arriba: number
  gridx: number
  gridy: number
  intervalosx: number
  intervalosy: number
}

export type Punto = {
  x: number
  y: number
}

export type Segmento = {
  x1: number
  y1: number
  x2: number
  y2: number
}

export type Material = {
  consistencia: number
  angulo: number
  pseco: number
  psaturado: number
  cohesion: number
}

export type Capa = {
  nombre: string
  contorno: Punto[]
  material: Material
}

export type Carga = {
  nombre: string
  xInicial: number
  xFinal: number
  fX: string
  fY: string
}

export type Centros = {
  inicioX: number
  inicioY: number
  desplazaX: number
  nradios: number
  numeroX: number
  numeroY: number
  distanciaX: number
  distanciaY: number
}

export type Radios = {
  id: string
  min: number
  max: number
  minCalc: number
  maxCalc: number
}

export type DatosCoef = {
  centroX: number
  centroY: number
  radio: number
  coeficiente: number
}

export type Analisis = {
  numCentroY: number
  numCentroX: number
  numRadio: number
  centroX: number
  centroY: number
  radio: number
  coefMin: number
  coefMax: number
  coeficientes: DatosCoef[]
}

export type TaludBase = {
  nombre: string
  codigo: number
  avance: number
  sinCargas: boolean
}

// Necesario en Paso 1
export type Talud1 = {
  nombre: string
  codigo: number
  avance: number
  sinCargas: boolean
  dimensiones?: Dimensiones
}

// Necesario en Paso 2
export type Talud2 = {
  nombre: string
  codigo: number
  avance: number
  sinCargas: boolean
  dimensiones: Dimensiones
  contorno?: Punto[]
}

// Necesario en Paso 3
export type Talud3 = {
  nombre: string
  codigo: number
  avance: number
  sinCargas: boolean
  dimensiones: Dimensiones
  contorno: Punto[]
  sinCapas?: boolean
  capas?: Capa[]
}

// Necesario en Recarga de Paso 3
export type Talud3r = {
  avance: number
  sinCapas?: boolean
  capas?: Capa[]
}

// Necesario en Paso 4
export type Talud4 = {
  nombre: string
  codigo: number
  avance: number
  sinCargas: boolean
  nombreMaterial: string
  capas: Capa[]
  material?: Material
}

// Necesario en Paso 5
export type Talud5 = {
  nombre: string
  codigo: number
  avance: number
  sinCargas: boolean
  dimensiones: Dimensiones
  nombreMaterial: string
  contorno: Punto[]
  sinCapas: boolean
  capas: Capa[]
  material: Material
  sinNivelFreatico?: boolean
  nivelFreatico?: Punto[]
}

// Necesario en Recarga de Paso 5
export type Talud5r = {
  avance: number
  sinNivelFreatico?: boolean
  nivelFreatico?: Punto[]
}

// Necesario en Paso 6
export type Talud6 = {
  nombre: string
  codigo: number
  avance: number
  sinCargas: boolean
  dimensiones: Dimensiones
  contorno: Punto[]
  cargas?: Carga[]
}

// Necesario en Recarga de Paso 6
export type Talud6r = {
  avance: number
  sinCargas: boolean
  cargas?: Carga[]
}

// Necesario en Paso 7
export type Talud7 = {
  nombre: string
  codigo: number
  avance: number
  sinCargas: boolean
  cargas: Carga[]
}

// Necesario en Paso 8
export type Talud8 = {
  nombre: string
  codigo: number
  avance: number
  sinCargas: boolean
  dimensiones: Dimensiones
  contorno: Punto[]
  centros?: Centros
}

// Necesario en Recarga de Paso 8
export type Talud8r = {
  avance: number
  centros?: Centros
}

// Necesario en Paso 9
export type Talud9 = {
  nombre: string
  codigo: number
  avance: number
  sinCargas: boolean
  dimensiones: Dimensiones
  contorno: Punto[]
  capas: Capa[]
  sinNivelFreatico: boolean
  nivelFreatico: Punto[]
  cargas: Carga[]
  centros: Centros
  radios?: Radios[]
}

// Necesario en Recarga de Paso 9
export type Talud9r = {
  avance: number
  radios?: Radios[]
}

// Necesario en Paso 10
export type Talud10 = {
  nombre: string
  codigo: number
  avance: number
  sinCargas: boolean
  dovelasX?: number
  dovelasAnchoMax?: number
  metodo?: number
}

// Necesario en Paso 11
export type Talud11 = {
  nombre: string
  codigo: number
  avance: number
  sinCargas: boolean
  dimensiones: Dimensiones
  contorno: Punto[]
  capas: Capa[]
  sinNivelFreatico: boolean
  nivelFreatico: Punto[]
  cargas: Carga[]
  centros: Centros
  radios: Radios[]
  dovelasX: number
  dovelasAnchoMax: number
  metodo: number
  analisis: Analisis
}

// Todos los datos completos
export type Talud = {
  nombre: string
  codigo: number
  avance: number
  sinCargas: boolean
  dimensiones: Dimensiones
  nombreMaterial: string
  contorno: Punto[]
  sinCapas: boolean
  capas: Capa[]
  material: Material
  sinNivelFreatico: boolean
  nivelFreatico: Punto[]
  cargas: Carga[]
  centros: Centros
  radios: Radios[]
  dovelasX: number
  dovelasAnchoMax: number
  metodo: number
  analisis: Analisis
}
