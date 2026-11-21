export const BLAD_ZAPISU = 'Nie udało się zapisać. Spróbuj ponownie.'

export const NAZWY_WERDYKTOW = {
  ok: 'OK',
  do_sprawdzenia: 'Do sprawdzenia',
  oszustwo: 'Oszustwo',
}

export function bezTekstu(reklama) {
  return reklama.tekst.trim() === ''
}

export const NAZWY_STATUSOW = {
  nowa: 'Nowa',
  w_toku: 'W toku',
  zamknieta: 'Zamknięta',
}

const NAZWY_ZRODEL = {
  google_ads: 'Google Ads',
  youtube: 'YouTube',
  meta_ads: 'Meta',
  strony_doradcow: 'Strony doradców',
  patrol_ostrzezen: 'Lista ostrzeżeń KNF',
  panel: 'Dodane ręcznie',
}

export const PLATFORMY = {
  google: 'Google Ads',
  facebook: 'Meta (Facebook / Instagram)',
  tiktok: 'TikTok',
  youtube: 'YouTube',
  www: 'Strona www',
  inna: 'Inna',
}

export const NAZWY_MODULOW = {
  M1: 'Monitoring ekosystemu zewnętrznego',
  M2: 'Zgodność i informacja o ryzyku',
  M3: 'Usługi nieautoryzowane',
}

export const NAZWY_LIST_KNF = {
  domy_maklerskie: 'dom maklerski',
  banki_maklerskie: 'bank maklerski',
  oddzialy_zagranicznych_firm: 'oddział zagranicznej firmy',
  notyfikowane_zagraniczne: 'notyfikowana firma zagraniczna',
}

// Ordered from the strongest finding to the weakest.
export const TAGI = {
  reklama_domeny_z_ostrzezenia_knf: 'Domena z ostrzeżeń KNF',
  druga_domena_ostrzezonej_strony: 'Kopia strony z ostrzeżeń',
  platnik_poza_listami: 'Płatnik poza listami KNF',
  doradztwo_bez_zezwolenia: 'Doradztwo bez zezwolenia',
  zysk_bez_ryzyka: 'Obietnica zysku',
  platnik_spoza_rejestru: 'Płatnik spoza rejestru KNF',
  podatki_bez_zastrzezenia: 'Podatki bez zastrzeżenia',
  wyniki_bez_zastrzezenia: 'Wyniki bez zastrzeżenia',
  test_zbieracza: 'Sygnał testowy',
}

export const TAGI_MODELU = {
  oszustwo: 'Tekst wygląda na oszustwo',
  do_sprawdzenia: 'Tekst budzi wątpliwości',
}

export function tag(sygnal) {
  if (TAGI[sygnal.kod]) return TAGI[sygnal.kod]
  if (sygnal.opis.length <= 40) return sygnal.opis
  const uciete = sygnal.opis.slice(0, 41)
  return uciete.slice(0, uciete.lastIndexOf(' ')).replace(/[,.;:]$/, '')
}

export function nazwaZrodla(zrodlo) {
  return NAZWY_ZRODEL[zrodlo] ?? zrodlo
}

export function domena(url) {
  if (!url) return null
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}

function dwie(liczba) {
  return String(liczba).padStart(2, '0')
}

export function data(iso) {
  const d = new Date(iso)
  return dwie(d.getDate()) + '.' + dwie(d.getMonth() + 1) + ' ' + dwie(d.getHours()) + ':' + dwie(d.getMinutes())
}

export function dzien(iso) {
  const d = new Date(iso)
  return d.getFullYear() + '-' + dwie(d.getMonth() + 1) + '-' + dwie(d.getDate())
}

export function dzienCzytelny(dzien) {
  return dzien.slice(8, 10) + '.' + dzien.slice(5, 7) + '.' + dzien.slice(0, 4)
}

export function liczba(n) {
  return n.toLocaleString('pl-PL')
}

function odmien(n, jedna, kilka, wiele) {
  const dziesiatki = n % 100
  const jednosci = n % 10
  if (n === 1) return '1 ' + jedna
  if (jednosci >= 2 && jednosci <= 4 && (dziesiatki < 12 || dziesiatki > 14)) return liczba(n) + ' ' + kilka
  return liczba(n) + ' ' + wiele
}

export function ileReklam(n) {
  return odmien(n, 'reklama', 'reklamy', 'reklam')
}

export function ileSpraw(n) {
  return odmien(n, 'sprawa', 'sprawy', 'spraw')
}
