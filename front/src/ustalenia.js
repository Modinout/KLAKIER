import { bezTekstu, liniaOszustwa, tag, TAG_MODELU, TAGI, tagModelu } from './nazwy.js'

// Notes, not findings about the ad: whether operators block the domain (CERT), and a payer that is
// a different company than the registered one with the same brand.
const KODY_NOTATEK = ['brak_na_liscie_cert', 'na_liscie_cert', 'platnik_spoza_rejestru']

// The text model's finding outranks findings about the payer alone.
const KOLEJNOSC_TAGOW = Object.values(TAGI).flatMap((t) => (t === TAGI.doradztwo_bez_zezwolenia ? [t, TAG_MODELU] : [t]))

export function ustalenia(reklama) {
  return reklama.sygnaly.filter((s) => !KODY_NOTATEK.includes(s.kod))
}

export function notatki(reklama) {
  return reklama.sygnaly.filter((s) => KODY_NOTATEK.includes(s.kod))
}

export function ocenaModelu(reklama) {
  if (bezTekstu(reklama) || reklama.werdykt !== 'oszustwo') return null
  return liniaOszustwa(reklama)
}

export function sila(t) {
  const i = KOLEJNOSC_TAGOW.indexOf(t)
  return i === -1 ? KOLEJNOSC_TAGOW.length : i
}

export function tagi(reklama) {
  const zSygnalow = [...new Set(ustalenia(reklama).map(tag))].sort((a, b) => sila(a) - sila(b))
  const model = ocenaModelu(reklama) && tagModelu(reklama)
  return [...zSygnalow, ...(model ? [model] : [])].slice(0, 3)
}
