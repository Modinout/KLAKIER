import { NAZWY_LIST_KNF } from './nazwy.js'

const KTO = {
  youtube: 'Kanał',
  strony_doradcow: 'Właściciel strony',
  patrol_ostrzezen: 'Właściciel strony',
}

// For these sources the name is the author, not a payer, so a match on the KNF lists is information only.
const AUTORZY = ['youtube', 'strony_doradcow']

export const STANY_REJESTRU = {
  w_rejestrze: 'na liście KNF',
  spoza_rejestru: 'inna spółka niż w rejestrze',
  poza_listami: 'brak na listach KNF',
  bank: 'bank, poza listami firm inwestycyjnych',
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

// A crypto-asset provider licensed in another EU state is found in the ESMA register, not on the KNF lists.
export function nazwaRejestru(rejestr) {
  return rejestr.lista === 'mica' ? 'W rejestrze MiCA' : 'W rejestrze KNF'
}

export function wpisRejestru(rejestr) {
  return [rejestr.panstwo, NAZWY_LIST_KNF[rejestr.lista] ?? rejestr.lista].filter(Boolean)
}
