import { domenaDocelowa, dzien, pierwszaDomena, TAG_MODELU } from './nazwy.js'
import { KOLEJNOSC } from './ryzyko.js'
import { ocenaModelu, sila, tagi, ustalenia } from './ustalenia.js'

export function dzienReklamy(reklama) {
  return reklama.opublikowano ?? dzien(reklama.zebrano)
}

function ostrzezonaDomena(reklama) {
  const sygnal = reklama.sygnaly.find((s) => s.kod === 'reklama_domeny_z_ostrzezenia_knf')
  if (!sygnal) return null
  return domenaDocelowa(reklama) ?? pierwszaDomena(sygnal.opis)
}

// Ads leading to a warned domain form one case whoever paid for them; otherwise one payer is one case.
export function klucz(reklama) {
  const ostrzezona = ostrzezonaDomena(reklama)
  if (ostrzezona) return 'knf|' + ostrzezona
  if (reklama.reklamodawca) return 'platnik|' + reklama.reklamodawca
  const cel = domenaDocelowa(reklama)
  return cel ? 'domena|' + cel : 'id|' + reklama.id
}

export function tytul(reklama) {
  return (
    ostrzezonaDomena(reklama) ??
    reklama.reklamodawca ??
    domenaDocelowa(reklama) ??
    pierwszaDomena(reklama.tekst) ??
    'Reklama bez nadawcy'
  )
}

function ileUstalen(reklama) {
  return ustalenia(reklama).length + (ocenaModelu(reklama) ? 1 : 0)
}

function odNajnowszej(a, b) {
  return dzienReklamy(b).localeCompare(dzienReklamy(a)) || b.zebrano.localeCompare(a.zebrano) || b.id - a.id
}

export function odNajgorszej(a, b) {
  return KOLEJNOSC[a.poziom] - KOLEJNOSC[b.poziom] || ileUstalen(b) - ileUstalen(a) || odNajnowszej(a, b)
}

export function sprawa(reklamy) {
  const posortowane = [...reklamy].sort(odNajgorszej)
  const glowna = posortowane[0]
  const najnowsza = [...reklamy].sort(odNajnowszej)[0]
  return {
    klucz: klucz(glowna),
    tytul: tytul(glowna),
    reklamy: posortowane,
    glowna,
    poziom: glowna.poziom,
    dzien: dzienReklamy(najnowsza),
  }
}

export function wSprawy(reklamy) {
  const grupy = Map.groupBy(reklamy, klucz)
  return [...grupy.values()].map(sprawa)
}

// Cases flagged only by the text model share one reason, whatever kind of fraud it names.
export function najmocniejszyTag(sprawa) {
  const reklama = sprawa.glowna
  if (ustalenia(reklama).length > 0) return tagi(reklama)[0]
  return ocenaModelu(reklama) ? TAG_MODELU : undefined
}

export function odNajgorszych(a, b) {
  return (
    KOLEJNOSC[a.poziom] - KOLEJNOSC[b.poziom] ||
    sila(najmocniejszyTag(a)) - sila(najmocniejszyTag(b)) ||
    b.dzien.localeCompare(a.dzien) ||
    b.glowna.id - a.glowna.id
  )
}
