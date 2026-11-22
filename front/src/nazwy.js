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
  reklama_domeny_z_ostrzezenia_knf: 'Strona jest na liście ostrzeżeń KNF',
  druga_domena_ostrzezonej_strony: 'Kopia strony z listy ostrzeżeń KNF',
  na_liscie_csirt_knf: 'Oszustwo zgłoszone przez CSIRT KNF',
  wielu_platnikow_domeny: 'Za jedną stronę płaci kilka firm',
  obca_domena: 'Znana firma reklamuje cudzą stronę',
  doradztwo_bez_zezwolenia: 'Doradza bez zezwolenia KNF',
  platnik_poza_listami: 'Firmy nie ma w rejestrach KNF',
  mloda_domena: 'Strona założona tuż przed reklamą',
  zysk_bez_ryzyka: 'Obiecuje zysk bez ryzyka',
  brak_ostrzezenia_cfd: 'CFD bez ostrzeżenia o stratach',
  ostrzezenie_nieczytelne: 'Ostrzeżenie o ryzyku trudno zauważyć',
  brak_ostrzezenia_strony: 'Strona nie ostrzega o ryzyku',
  polecenie_bez_oznaczenia: 'Link polecający bez oznaczenia reklamy',
  podatki_bez_zastrzezenia: 'Korzyść podatkowa bez zastrzeżenia',
  wyniki_bez_zastrzezenia: 'Dawne zyski bez zastrzeżenia',
  nadzor_jako_argument: 'Zachwala się nadzorem KNF',
  test_zbieracza: 'Sygnał testowy',
}

export const TAG_MODELU = 'Tekst jak w fałszywych inwestycjach'

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

export function zdanieZapisu(n) {
  if (n === 0) return 'Przy tym progu żadna reklama z bazy nie zmieni poziomu.'
  const ile = ileReklam(n)
  return 'Przy tym progu wysokie ryzyko ' + (ile.endsWith('reklamy') ? 'dostaną ' : 'dostanie ') + ile + ' z bazy.'
}

export const NAZWY_POWIAZAN = {
  ten_sam_telefon: 'Ten sam numer telefonu',
  ten_sam_komunikator: 'Ten sam kontakt w komunikatorze',
}

export function ilePrzeoczonych(n) {
  return odmien(n, 'przeoczone oszustwo', 'przeoczone oszustwa', 'przeoczonych oszustw')
}

export function ileAlarmow(n) {
  return odmien(n, 'fałszywy alarm', 'fałszywe alarmy', 'fałszywych alarmów')
}

export const OPISY = {
  alerty: 'Sprawy wysokiego ryzyka.',
  kalibracja: 'Tu sprawdzasz, jak model KAPSEL oceniający tekst reklam zachowuje się przy różnych progach.',
  suwak:
    'Suwak pokazuje symulację na zbiorze testowym. Przycisk zapisuje próg: reklamy, którym model KAPSEL dał co najmniej takie ryzyko, dostają wysoki poziom. Twarde ustalenia, takie jak domena z listy ostrzeżeń KNF, nie zależą od progu.',
  ucz: 'Gdy ustawisz lub poprawisz ocenę tekstu w szczegółach sprawy, możesz tu douczyć model i ponownie ocenić wszystkie reklamy w bazie.',
  uczPusto: 'Brak ocen do nauki. Otwórz sprawę i ustaw lub popraw ocenę tekstu, aby odblokować przycisk.',
  dodaj: 'Wklej tekst reklamy albo wrzuć jej zrzut. Reklama trafi do kolejki od razu z oceną.',
}
