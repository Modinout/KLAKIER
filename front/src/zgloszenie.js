import { adresObrazu } from './api.js'
import { bezTekstu, data, domenaDocelowa, dzien, dzienCzytelny, nazwaZrodla } from './nazwy.js'
import { kto, STANY_REJESTRU, stanRejestru, wpisRejestru } from './rejestr.js'
import { POZIOMY } from './ryzyko.js'
import { tytul } from './sprawy.js'
import { notatki, ocenaModelu, ustalenia, zdaniePowodu } from './ustalenia.js'

const NAGLOWEK = 'Zgłoszenie sprawy: '
const SPORZADZONO = 'Sporządzono: '
const REKLAM_W_SPRAWIE = 'Reklamy w sprawie: '
const RYZYKO = ' ryzyko'
const PROWADZI_DO = 'Prowadzi do: '
const W_REJESTRZE = 'W rejestrze KNF: '
const REKLAMA_NR = 'Reklama nr '
const ZRODLO = 'Źródło: '
const ZEBRANO = 'Zebrano: '
const ADRES = 'Adres: '
const OBRAZ = 'Obraz: '
const USTALENIA = 'Ustalenia:'
const PODSTAWA = '   Podstawa: '
const UWAGI = 'Uwagi:'
const TRESC = 'Treść:'
const BEZ_TEKSTU = 'Reklama graficzna, tekst nie został odczytany'

function rozne(lista) {
  return [...new Set(lista.filter(Boolean))]
}

function wniosek(reklama) {
  const zdanie = zdaniePowodu(reklama)
  return POZIOMY[reklama.poziom] + RYZYKO + (zdanie ? ': ' + zdanie : '')
}

function platnicy(reklamy) {
  return rozne(reklamy.map((r) => r.reklamodawca)).map((nazwa) => {
    const reklama = reklamy.find((r) => r.reklamodawca === nazwa)
    const stan = stanRejestru(reklama)
    return kto(reklama) + ': ' + nazwa + (stan ? ' (' + STANY_REJESTRU[stan] + ')' : '')
  })
}

function podmioty(reklamy) {
  const wpisy = reklamy.filter((r) => r.rejestr?.podmiot).map((r) => [r.rejestr.podmiot, ...wpisRejestru(r.rejestr)].join(', '))
  return rozne(wpisy).map((wpis) => W_REJESTRZE + wpis)
}

function listaUstalen(reklama) {
  const punkty = ustalenia(reklama).map((s) => s.opis + (s.podstawa ? '\n' + PODSTAWA + s.podstawa : ''))
  const model = ocenaModelu(reklama)
  if (model) punkty.push(model)
  if (punkty.length === 0) return []
  return [USTALENIA, ...punkty.map((p, i) => i + 1 + '. ' + p)]
}

function blokReklamy(reklama) {
  const uwagi = notatki(reklama)
  return [
    REKLAMA_NR + reklama.id,
    ZRODLO + nazwaZrodla(reklama.zrodlo),
    ZEBRANO + data(reklama.zebrano),
    reklama.url && ADRES + reklama.url,
    reklama.ma_obraz && OBRAZ + new URL(adresObrazu(reklama.id), location.origin).href,
    ...listaUstalen(reklama),
    ...(uwagi.length ? [UWAGI, ...uwagi.map((s) => '- ' + s.opis)] : []),
    TRESC,
    bezTekstu(reklama) ? BEZ_TEKSTU : reklama.tekst,
  ]
}

function blok(linie) {
  return linie.filter(Boolean).join('\n')
}

// The first ad is the one open on the sheet.
export function zgloszenie(reklamy) {
  const glowna = reklamy[0]
  const bloki = [
    [NAGLOWEK + tytul(glowna), SPORZADZONO + dzienCzytelny(dzien(new Date())), REKLAM_W_SPRAWIE + reklamy.length],
    [wniosek(glowna)],
    [...platnicy(reklamy), ...rozne(reklamy.map(domenaDocelowa)).map((d) => PROWADZI_DO + d), ...podmioty(reklamy)],
    ...reklamy.map(blokReklamy),
  ]
  return bloki.map(blok).filter(Boolean).join('\n\n')
}

export function nazwaPliku(reklamy) {
  return 'zgloszenie_' + tytul(reklamy[0]).toLowerCase().replace(/[^a-z0-9.-]/g, '_') + '_' + dzien(new Date()) + '.txt'
}
