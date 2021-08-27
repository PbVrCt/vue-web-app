export const enum MetodoNum {
  Fellenius = 1,
  Bishop,
  Spencer,
  MorgerstenPrice,
  Janbu,
  Celestino
}

export const metodosTex: { [index in MetodoNum]: string } = {
  [MetodoNum.Fellenius]: 'Método de Fellenius',
  [MetodoNum.Bishop]: 'Método de Bishop',
  [MetodoNum.Spencer]: 'Método de Spencer',
  [MetodoNum.MorgerstenPrice]: 'Método de Morgersten y Price',
  [MetodoNum.Janbu]: 'Método de Janbu',
  [MetodoNum.Celestino]: 'Método de Celestino'
}
