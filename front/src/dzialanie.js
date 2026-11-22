import { polecanaFirma } from './rejestr.js'
import { ustalenia } from './ustalenia.js'

export const KROTKO = {
  platforma: 'Zgłoś platformie i CERT',
  broker: 'Napisz do brokera',
  firma: 'Napisz do firmy',
  sprawdz: 'Sprawdź ręcznie',
  nic: 'Nic',
}

// Co urzędnik ma zrobić ze sprawą; decyduje główna reklama sprawy.
export function rodzaj(reklama) {
  if (reklama.poziom === 'wysokie') return 'platforma'
  if (polecanaFirma(reklama)) return 'broker'
  if (ustalenia(reklama).some((s) => s.modul === 'M2')) return 'firma'
  if (reklama.poziom === 'srednie') return 'sprawdz'
  return 'nic'
}
