import { NAZWY_LIST_KNF } from './nazwy.js'

const KTO = {
  youtube: 'Kanał',
  strony_doradcow: 'Właściciel strony',
  patrol_ostrzezen: 'Właściciel strony',
}

// Dla tych źródeł nazwa to autor, a nie płatnik, więc trafienie w rejestrach KNF ma tylko charakter informacyjny.
const AUTORZY = ['youtube', 'strony_doradcow']

export const STANY_REJESTRU = {
  w_rejestrze: 'w rejestrze KNF',
  spoza_rejestru: 'inna spółka niż w rejestrze',
  poza_listami: 'brak w rejestrach KNF',
  bank: 'bank, poza rejestrami firm inwestycyjnych',
  mica: 'licencja MiCA w innym kraju UE',
}

export function kto(reklama) {
  return KTO[reklama.zrodlo] ?? 'Zapłacił'
}

export function stanRejestru(reklama) {
  const rejestr = reklama.rejestr
  if (!AUTORZY.includes(reklama.zrodlo)) return STANY_REJESTRU[rejestr?.stan] ? rejestr.stan : null
  if (rejestr?.stan === 'w_rejestrze' || (rejestr?.stan === 'spoza_rejestru' && rejestr.podmiot)) return 'w_rejestrze'
  return null
}

// Dostawca kryptoaktywów z licencją w innym państwie UE jest w rejestrze ESMA, a nie w rejestrach KNF.
export function nazwaRejestru(rejestr) {
  return rejestr.lista === 'mica' ? 'W rejestrze MiCA' : 'W rejestrze KNF'
}

export function wpisRejestru(rejestr) {
  return [rejestr.panstwo, NAZWY_LIST_KNF[rejestr.lista] ?? rejestr.lista].filter(Boolean)
}
