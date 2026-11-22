import { bezTekstu, data, domenaDocelowa, dzien, dzienCzytelny, nazwaZrodla } from './nazwy.js'
import { kto, nazwaRejestru, STANY_REJESTRU, stanRejestru, wpisRejestru } from './rejestr.js'
import { POZIOMY } from './ryzyko.js'
import { tytul } from './sprawy.js'
import { notatki, ocenaModelu, ustalenia, zdaniePowodu } from './ustalenia.js'

const NAGLOWEK = 'Zgłoszenie sprawy: '
const SPORZADZONO = 'Sporządzono: '
const REKLAM_W_SPRAWIE = 'Reklamy w sprawie: '
const RYZYKO = ' ryzyko'
const PROWADZI_DO = 'Prowadzi do: '
const REKLAMA_NR = 'Reklama nr '
const ZEBRANO = 'zebrano '
const ADRES = 'Adres: '
const USTALENIA = 'Ustalenia:'
const PODSTAWA = '   Podstawa: '
const UWAGI = 'Uwagi:'
const TRESC = 'Treść: '
const Z_OBRAZKA = 'Tekst odczytany z obrazka: '
const NOTATKA = 'Notatka: '
const BEZ_TEKSTU ='Reklama graficzna, tekst nie został odczytany'

function rozne(lista) {
  return [...new Set(lista.filter(Boolean))]
}

// Powód jest pomijany, gdy pierwsze ustalenie sprawy już go mówi.
function wniosek(reklama, pierwszyPunkt) {
  const zdanie = zdaniePowodu(reklama)
  const powtorzone = zdanie && pierwszyPunkt && zdanie.startsWith(pierwszyPunkt.split('\n')[0])
  return POZIOMY[reklama.poziom] + RYZYKO + (zdanie && !powtorzone ? ': ' + zdanie : '')
}

function zdania(tekst) {
  return tekst.split(/(?<=\.) (?=\p{Lu})/u)
}

function punkt(s) {
  return s.opis + (s.podstawa ? '\n' + PODSTAWA + s.podstawa : '')
}

function takieSamo(a, b) {
  return a.kod === b.kod && (a.podstawa ?? null) === (b.podstawa ?? null)
}

// Ustalenie jest wspólne, gdy każda reklama ma je z tym samym kodem i podstawą; sprawa trzyma
// zdania, które mówią wszystkie, a każda reklama zachowuje resztę własnego opisu.
function wspolneUstalenia(reklamy) {
  return ustalenia(reklamy[0]).flatMap((s) => {
    const takie = reklamy.map((r) => ustalenia(r).find((t) => takieSamo(s, t)))
    if (takie.some((t) => !t)) return []
    const wszystkich = zdania(s.opis).filter((z) => takie.every((t) => zdania(t.opis).includes(z)))
    return wszystkich.length ? [{ ...s, opis: wszystkich.join(' ') }] : []
  })
}

function resztaOpisow(reklama, wspolneU) {
  return wspolneU.map((w) => {
    const wlasne = ustalenia(reklama).find((t) => takieSamo(w, t))
    return zdania(wlasne.opis).filter((z) => !zdania(w.opis).includes(z)).join(' ')
  })
}

function platnicy(reklamy) {
  return rozne(reklamy.map((r) => r.reklamodawca)).map((nazwa) => {
    const reklama = reklamy.find((r) => r.reklamodawca === nazwa)
    const stan = stanRejestru(reklama)
    return kto(reklama) + ': ' + nazwa + (stan ? ' (' + STANY_REJESTRU[stan] + ')' : '')
  })
}

function podmioty(reklamy) {
  const wpisy = reklamy
    .filter((r) => r.rejestr?.podmiot)
    .map((r) => nazwaRejestru(r.rejestr) + ': ' + [r.rejestr.podmiot, ...wpisRejestru(r.rejestr)].join(', '))
  return rozne(wpisy)
}

function punkty(reklama, wspolneU) {
  const lista = ustalenia(reklama).filter((t) => !wspolneU.some((w) => takieSamo(w, t))).map(punkt)
  const model = ocenaModelu(reklama)
  return model ? [...lista, model] : lista
}

function uwagi(reklama) {
  return notatki(reklama).map((s) => s.opis)
}

function wspolne(reklamy, lista) {
  return lista(reklamy[0]).filter((p) => reklamy.every((r) => lista(r).includes(p)))
}

function listaUstalen(lista) {
  return lista.length ? [USTALENIA, ...lista.map((p, i) => i + 1 + '. ' + p)] : []
}

function listaUwag(lista) {
  return lista.length ? [UWAGI, ...lista.map((p) => '- ' + p)] : []
}

// Ustalenia wspólne dla wszystkich reklam sprawy są wymienione raz nad reklamami.
function blokReklamy(reklama, wspolneU, wspolnePunkty, wspolneUwagi) {
  return [
    [REKLAMA_NR + reklama.id, nazwaZrodla(reklama.zrodlo), ZEBRANO + data(reklama.zebrano)].join(' · '),
    ...resztaOpisow(reklama, wspolneU),
    reklama.url && ADRES + reklama.url,
    ...listaUstalen(punkty(reklama, wspolneU).filter((p) => !wspolnePunkty.includes(p))),
    ...listaUwag(uwagi(reklama).filter((p) => !wspolneUwagi.includes(p))),
    bezTekstu(reklama) ? TRESC + BEZ_TEKSTU : (reklama.ma_obraz ? Z_OBRAZKA : TRESC) + jedenAkapit(reklama.tekst),
    reklama.notatka && NOTATKA + jedenAkapit(reklama.notatka),
  ]
}

function jedenAkapit(tekst) {
  return tekst.replace(/\s+/g, ' ').trim()
}

function blok(linie) {
  return linie.filter(Boolean).join('\n')
}

// Pierwsza reklama to ta otwarta w szczegółach.
export function zgloszenie(reklamy) {
  const glowna = reklamy[0]
  const wspolneU = wspolneUstalenia(reklamy)
  const wspolnePunkty = wspolne(reklamy, (r) => punkty(r, wspolneU))
  const wspolneUwagi = wspolne(reklamy, uwagi)
  const punktySprawy = [...wspolneU.map(punkt), ...wspolnePunkty]
  const bloki = [
    [NAGLOWEK + tytul(glowna), SPORZADZONO + dzienCzytelny(dzien(new Date())), REKLAM_W_SPRAWIE + reklamy.length],
    [wniosek(glowna, punktySprawy[0])],
    [...platnicy(reklamy), ...rozne(reklamy.map(domenaDocelowa)).map((d) => PROWADZI_DO + d), ...podmioty(reklamy)],
    [...listaUstalen(punktySprawy), ...listaUwag(wspolneUwagi)],
    ...reklamy.map((r) => blokReklamy(r, wspolneU, wspolnePunkty, wspolneUwagi)),
  ]
  return bloki.map(blok).filter(Boolean).join('\n\n')
}

export function nazwaPliku(reklamy) {
  return 'zgloszenie_' + tytul(reklamy[0]).toLowerCase().replace(/[^a-z0-9.-]/g, '_') + '_' + dzien(new Date()) + '.txt'
}
