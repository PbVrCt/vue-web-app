// Obtener Cookie por nombre
export function getCookie(name: string) {
  const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)')
  return v ? v[2] : null
}
