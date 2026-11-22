import { bezTekstu, data, domenaDocelowa, dzien, dzienCzytelny, NAZWY_STATUSOW, nazwaZrodla } from './nazwy.js'
import { STANY_REJESTRU, stanRejestru, wpisRejestru } from './rejestr.js'
import { POZIOMY } from './ryzyko.js'
import { ocenaModelu, ustalenia, zdaniePowodu } from './ustalenia.js'

const KOLUMNY = [
  'Sprawa',
  'Nr reklamy',
  'Ryzyko',
  'Powód',
  'Moduły',
  'Ustalenia',
  'Reklamodawca',
  'Stan w rejestrze KNF',
  'Firma w rejestrze KNF',
  'Prowadzi do',
  'Adres',
  'Źródło',
  'Treść',
  'Opublikowano',
  'Zebrano',
  'Status',
]

const PODSTAWA = ' (Podstawa: '

function listaUstalen(reklama) {
  const punkty = ustalenia(reklama).map((s) => s.opis + (s.podstawa ? PODSTAWA + s.podstawa + ')' : ''))
  const model = ocenaModelu(reklama)
  if (model) punkty.push(model)
  return punkty.join(' | ')
}

function wiersz(sprawa, reklama) {
  const stan = stanRejestru(reklama)
  return [
    sprawa.tytul,
    reklama.id,
    POZIOMY[reklama.poziom],
    zdaniePowodu(reklama),
    [...new Set(ustalenia(reklama).map((s) => s.modul))].join(', '),
    listaUstalen(reklama),
    reklama.reklamodawca,
    stan ? STANY_REJESTRU[stan] : '',
    reklama.rejestr?.podmiot ? [reklama.rejestr.podmiot, ...wpisRejestru(reklama.rejestr)].join(', ') : '',
    domenaDocelowa(reklama),
    reklama.url,
    nazwaZrodla(reklama.zrodlo),
    bezTekstu(reklama) ? '' : reklama.tekst.replace(/\s+/g, ' ').trim(),
    reklama.opublikowano ? dzienCzytelny(reklama.opublikowano) : '',
    data(reklama.zebrano),
    NAZWY_STATUSOW[reklama.status],
  ]
}

// Początkowy znak = + - @, tabulator albo powrót karetki sprawiłby, że arkusz wykona tekst reklamy jako formułę.
function komorka(wartosc) {
  const tekst = String(wartosc ?? '')
  const bezpieczny = /^[=+\-@\t\r]/.test(tekst) ? "'" + tekst : tekst
  return '"' + bezpieczny.replaceAll('"', '""') + '"'
}

export function raport(sprawy) {
  const wiersze = [KOLUMNY, ...sprawy.flatMap((s) => s.reklamy.map((r) => wiersz(s, r)))]
  return '﻿' + wiersze.map((w) => w.map(komorka).join(';') + '\r\n').join('')
}

export function nazwaRaportu() {
  return 'klakier_raport_' + dzien(new Date()) + '.csv'
}
