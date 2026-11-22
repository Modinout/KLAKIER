import { domenaDocelowa, dzienCzytelny, nazwaZrodla, tag } from './nazwy.js'
import { polecanaFirma } from './rejestr.js'
import { tytul } from './sprawy.js'
import { sila, ustalenia, zdaniePowodu } from './ustalenia.js'

// Tylko te źródła to platformy, które same usuwają reklamy.
const PLATFORMY = { google_ads: 'Google', meta_ads: 'Meta', tiktok_ads: 'TikTok', youtube: 'YouTube' }

function rozne(lista) {
  return [...new Set(lista.filter(Boolean))]
}

function blok(linie) {
  return linie.filter(Boolean).join('\n')
}

function gdzie(reklama) {
  return reklama.url ?? 'reklama nr ' + reklama.id
}

function pierwszeWyswietlenie(reklama) {
  return reklama.opublikowano && 'pierwsze wyświetlenie ' + dzienCzytelny(reklama.opublikowano)
}

function zPodstawa(s) {
  return s.opis + (s.podstawa ? ' (podstawa: ' + s.podstawa + ')' : '')
}

function maKod(reklama, kod) {
  return reklama.sygnaly.some((s) => s.kod === kod)
}

function najmocniejsze(reklama) {
  return [...ustalenia(reklama)].sort((a, b) => sila(tag(a)) - sila(tag(b)))[0]
}

function doPlatformy(reklamy) {
  const glowna = reklamy[0]
  const platformy = rozne(reklamy.map((r) => PLATFORMY[r.zrodlo]))
  const domena = domenaDocelowa(glowna)
  return [
    ['Zgłoszenie reklam: ' + tytul(glowna)],
    [
      platformy.length && 'Prośba do ' + platformy.join(', ') + ': usunięcie reklam wymienionych niżej.',
      domena && 'Prośba do CERT Polska: wpisanie domeny ' + domena + ' na listę ostrzeżeń przed niebezpiecznymi stronami.',
    ],
    [
      glowna.powod && 'Powód: ' + zdaniePowodu(glowna),
      najmocniejsze(glowna)?.podstawa && 'Podstawa: ' + najmocniejsze(glowna).podstawa,
      maKod(glowna, 'platnik_poza_listami') &&
        !maKod(glowna, 'reklama_domeny_z_ostrzezenia_knf') &&
        'Firmy nie ma w rejestrach KNF ani na liście ostrzeżeń KNF. To może być podstawa do zawiadomienia prokuratury i wpisu na listę ostrzeżeń KNF.',
    ],
    [
      'Reklamy (' + reklamy.length + '):',
      ...reklamy.map(
        (r) =>
          '- ' +
          [gdzie(r), nazwaZrodla(r.zrodlo), r.reklamodawca && 'płatnik: ' + r.reklamodawca, pierwszeWyswietlenie(r)]
            .filter(Boolean)
            .join(', ')
      ),
      reklamy.some((r) => r.zrodlo === 'panel') && 'Dowody: zrzuty strony i jej kod z sumami SHA-256 w paczce dowodów',
    ],
  ]
}

function doFirmy(reklamy) {
  const glowna = reklamy[0]
  const zrodlo = [nazwaZrodla(glowna.zrodlo), pierwszeWyswietlenie(glowna)].filter(Boolean).join(', ')
  // To samo naruszenie w kilku reklamach różni się tylko cytatem, więc liczy się raz.
  const wszystkie = reklamy.flatMap((r) => ustalenia(r).filter((s) => s.modul === 'M2'))
  const naruszenia = wszystkie
    .filter((s, i) => wszystkie.findIndex((t) => t.kod === s.kod && t.podstawa === s.podstawa) === i)
    .map(zPodstawa)
  return [
    [
      'Do: ' + (glowna.rejestr?.podmiot ?? glowna.reklamodawca ?? ''),
      'Dotyczy: reklamy ' + (glowna.url ?? 'nr ' + glowna.id) + ' (' + zrodlo + ')',
    ],
    [
      'Dzień dobry,',
      'w tej reklamie znaleźliśmy niezgodności:',
      ...naruszenia.map((n, i) => i + 1 + '. ' + n),
      'Prosimy o poprawienie reklamy i informację zwrotną.',
    ],
  ]
}

function doBrokera(reklamy) {
  const glowna = reklamy[0]
  const firma = polecanaFirma(glowna)
  const polecenie = glowna.sygnaly.find((s) => s.kod === 'polecenie_bez_oznaczenia' && s.firma)
  return [
    [
      'Do: ' + firma.nazwa,
      'Dotyczy: link polecający do ' + firma.domena + ' w materiale autora „' + tytul(glowna) + '”' + (glowna.url ? ' (' + glowna.url + ')' : ''),
    ],
    [
      'Dzień dobry,',
      'ten materiał promuje Państwa usługi linkiem polecającym, ale nie jest oznaczony jako reklama.',
      zPodstawa(polecenie),
      'Prosimy o sprawdzenie współpracy z autorem i o oznaczanie takich materiałów jako reklamy.',
    ],
  ]
}

const PISMA = { platforma: doPlatformy, firma: doFirmy, broker: doBrokera }

// Pierwsza reklama to główna reklama sprawy.
export function pismo(rodzaj, reklamy) {
  return PISMA[rodzaj](reklamy).map(blok).filter(Boolean).join('\n\n')
}
