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
  csirt_knf: 'CSIRT KNF',
  tiktok_ads: 'TikTok',
  plik: 'Plik',
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
  na_liscie_csirt_knf: 'Oszustwo z listy CSIRT KNF',
  wielu_platnikow_domeny: 'Wielu płatników jednej domeny',
  obca_domena: 'Marka z rejestru, obca domena',
  doradztwo_bez_zezwolenia: 'Doradztwo bez zezwolenia',
  platnik_poza_listami: 'Płatnik poza listami KNF',
  zysk_bez_ryzyka: 'Obietnica zysku',
  brak_ostrzezenia_cfd: 'Brak ostrzeżenia o stratach na CFD',
  podatki_bez_zastrzezenia: 'Podatki bez zastrzeżenia',
  wyniki_bez_zastrzezenia: 'Wyniki bez zastrzeżenia',
  nadzor_jako_argument: 'Nadzór KNF jako argument',
  test_zbieracza: 'Sygnał testowy',
}

export const TAG_MODELU = 'Treść typowa dla fałszywych inwestycji'

function skroc(opis) {
  if (opis.length <= 40) return opis
  const uciete = opis.slice(0, 41)
  return uciete.slice(0, uciete.lastIndexOf(' ')).replace(/[,.;:]$/, '')
}

function zWielkiej(tekst) {
  return tekst.charAt(0).toUpperCase() + tekst.slice(1)
}

export function tag(sygnal) {
  return TAGI[sygnal.kod] ?? sygnal.opis
}

export function tagModelu(reklama) {
  const rodzaj = reklama.rodzaj?.trim()
  return rodzaj ? zWielkiej(skroc(rodzaj)) : TAG_MODELU
}

export function liniaOszustwa(reklama) {
  const rodzaj = reklama.rodzaj?.trim()
  return rodzaj ? TAG_MODELU + ': ' + zWielkiej(rodzaj) : TAG_MODELU
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

const BIBLIOTEKI = ['adstransparency.google.com', 'library.tiktok.com']

// An ad library page shows the ad itself, not where the ad leads.
export function zBiblioteki(url) {
  return BIBLIOTEKI.includes(domena(url)) || url.includes('facebook.com/ads/library')
}

export function domenaDocelowa(reklama) {
  if (reklama.domena) return reklama.domena.replace(/^www\./, '')
  if (reklama.url && !zBiblioteki(reklama.url)) return domena(reklama.url)
  return null
}

// One case of letters in the ending, so "dywidendy.Skorzystaj" is not taken for a domain.
const DOMENA = /\b(?:[A-Za-z0-9-]+\.)+(?:[a-z]{2,}|[A-Z]{2,})\b/

export function pierwszaDomena(tekst) {
  const znaleziona = tekst.match(DOMENA)
  return znaleziona && znaleziona[0].replace(/^www\./i, '').toLowerCase()
}

function dwie(liczba) {
  return String(liczba).padStart(2, '0')
}

export function data(iso) {
  const d = new Date(iso)
  return dzienCzytelny(dzien(d)) + ' ' + dwie(d.getHours()) + ':' + dwie(d.getMinutes())
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

export const OPISY = {
  analityka:
    'Reklamy inwestycyjne zebrane automatycznie i sprawdzone w rejestrach KNF. Najgroźniejsze sprawy są na górze: otwórz, przeczytaj ustalenia i zdecyduj.',
  alerty: 'Sprawy wysokiego ryzyka. „Nowe” to te, które doszły, odkąd panel jest otwarty.',
  kalibracja:
    'Tu sprawdzasz, jak czuły jest model, który czyta tekst reklam. Niższy próg łapie więcej oszustw, ale daje więcej fałszywych alarmów. Wyższy odwrotnie.',
  suwak: 'Suwak pokazuje, co by się zmieniło przy innym progu. Nie zmienia ocen spraw w kolejce.',
  twarde: 'Twarde ustalenia, takie jak domena z listy ostrzeżeń KNF albo płatnik poza listami KNF, nie zależą od progu.',
  ucz: 'Model uczy się z ocen tekstu poprawionych przez analityków i ocenia reklamy od nowa.',
  rodzaj: 'Dodaje nowy rodzaj fałszywej inwestycji, który model ma rozpoznawać.',
  dodaj: 'Wklej tekst reklamy albo wrzuć jej zrzut. Reklama trafi do kolejki od razu z oceną.',
}
