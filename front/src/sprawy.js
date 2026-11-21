import { domena, dzien } from './nazwy.js'
import { KOLEJNOSC } from './ryzyko.js'

export function dzienReklamy(reklama) {
  return reklama.opublikowano ?? dzien(reklama.zebrano)
}

export function klucz(reklama) {
  return reklama.reklamodawca + '|' + domena(reklama.url)
}

function odNajnowszej(a, b) {
  return dzienReklamy(b).localeCompare(dzienReklamy(a)) || b.zebrano.localeCompare(a.zebrano) || b.id - a.id
}

export function sprawa(reklamy) {
  const posortowane = [...reklamy].sort(odNajnowszej)
  const najgorsza = [...posortowane].sort((a, b) => KOLEJNOSC[a.poziom] - KOLEJNOSC[b.poziom])[0]
  return {
    klucz: klucz(posortowane[0]),
    reklamy: posortowane,
    glowna: posortowane[0],
    najgorsza,
    poziom: najgorsza.poziom,
    dzien: dzienReklamy(posortowane[0]),
  }
}

export function wSprawy(reklamy) {
  const grupy = Map.groupBy(reklamy, klucz)
  return [...grupy.values()].map(sprawa)
}

export function odNajgorszych(a, b) {
  return KOLEJNOSC[a.poziom] - KOLEJNOSC[b.poziom] || b.dzien.localeCompare(a.dzien) || b.glowna.id - a.glowna.id
}
