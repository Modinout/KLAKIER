import { bezTresci, liniaOszustwa, tag, TAG_MODELU, TAGI, tagModelu } from './nazwy.js'

// Uwagi, a nie ustalenia o reklamie: czy operatorzy blokują domenę (CERT) oraz płatnik, który
// jest inną firmą niż zarejestrowana z tą samą marką.
const KODY_NOTATEK = ['brak_na_liscie_cert', 'na_liscie_cert', 'platnik_spoza_rejestru']

// Ustalenie modelu tekstu ma pierwszeństwo przed ustaleniami samego płatnika.
const KOLEJNOSC_TAGOW = Object.values(TAGI).flatMap((t) => (t === TAGI.doradztwo_bez_zezwolenia ? [t, TAG_MODELU] : [t]))

export function ustalenia(reklama) {
  return reklama.sygnaly.filter((s) => !KODY_NOTATEK.includes(s.kod))
}

export function notatki(reklama) {
  return reklama.sygnaly.filter((s) => KODY_NOTATEK.includes(s.kod))
}

// O ustaleniu decyduje próg z Kalibracji, a nie werdykt, który model liczy ze stałym progiem.
export function ocenaModelu(reklama) {
  return reklama.ponad_progiem ? liniaOszustwa(reklama) : null
}

export function modelZalecaSprawdzenie(reklama) {
  return !bezTresci(reklama) && !reklama.ponad_progiem && (reklama.werdykt === 'do_sprawdzenia' || reklama.werdykt === 'oszustwo')
}

// Etykieta modelu jest najmocniejsza tylko wtedy, gdy żadna reguła nic nie ustaliła.
export function zdecydowalModel(reklama) {
  return Boolean(ocenaModelu(reklama)) && ustalenia(reklama).length === 0
}

export function czystaSprawa(reklama) {
  return reklama.poziom === 'niskie' && ustalenia(reklama).length === 0 && !ocenaModelu(reklama) && !modelZalecaSprawdzenie(reklama)
}

export function zdaniePowodu(reklama) {
  return reklama.powod && reklama.powod.replace(/^Tekst reklamy wygląda na oszustwo/, liniaOszustwa(reklama))
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
