import { bezTekstu } from './nazwy.js'
import { ustalenia } from './ustalenia.js'

export const POZIOMY = {
  wysokie: 'Wysokie',
  srednie: 'Średnie',
  niskie: 'Niskie',
}

export const KOLEJNOSC = { wysokie: 0, srednie: 1, niskie: 2 }

export function poziomRyzyka(reklama, prog) {
  const model = !bezTekstu(reklama)
  const ile = ustalenia(reklama).length
  if ((model && reklama.ryzyko >= prog) || ile >= 2) return 'wysokie'
  if (ile === 1 || (model && reklama.werdykt === 'do_sprawdzenia')) return 'srednie'
  return 'niskie'
}
