import { bezTekstu, liniaOszustwa, tag, TAGI, tagModelu } from './nazwy.js'

// CERT notes say whether operators block the domain; they are not findings about the ad.
export const KODY_CERT = ['brak_na_liscie_cert', 'na_liscie_cert']

const KOLEJNOSC_TAGOW = Object.values(TAGI)

export function ustalenia(reklama) {
  return reklama.sygnaly.filter((s) => !KODY_CERT.includes(s.kod))
}

export function notatkiCert(reklama) {
  return reklama.sygnaly.filter((s) => KODY_CERT.includes(s.kod))
}

export function ocenaModelu(reklama) {
  if (bezTekstu(reklama)) return null
  if (reklama.werdykt === 'oszustwo') return liniaOszustwa(reklama)
  if (reklama.werdykt === 'do_sprawdzenia') return 'Tekst reklamy budzi wątpliwości'
  return null
}

function sila(t) {
  const i = KOLEJNOSC_TAGOW.indexOf(t)
  return i === -1 ? KOLEJNOSC_TAGOW.length : i
}

export function tagi(reklama) {
  const zSygnalow = [...new Set(ustalenia(reklama).map(tag))].sort((a, b) => sila(a) - sila(b))
  const model = ocenaModelu(reklama) && tagModelu(reklama)
  return [...zSygnalow, ...(model ? [model] : [])].slice(0, 3)
}
