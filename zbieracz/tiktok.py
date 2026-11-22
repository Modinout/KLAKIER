# Reklamy TikToka wyświetlane w Polsce, pasujące do frazy, czytane z publicznej biblioteki treści komercyjnych TikToka.
# Użycie: python tiktok.py [fraza ...]; bez fraz przeszukuje krótką listę fraz inwestycyjnych.
import sys
import time
from datetime import datetime, timezone
from urllib.parse import quote, urlsplit

import rotacja
import wysylka

BIBLIOTEKA = 'https://library.tiktok.com'
FRAZY = ['inwestowanie', 'forex', 'kryptowaluty', 'giełda', 'trading']
NAJWIECEJ = 10
MIESIAC_MS = 30 * 24 * 3600 * 1000
# Tematy do odrzucenia, a nie do przyjęcia, bo etykieta tematu TikToka jest zawodna:
# ta sama reklama dostaje Financial Services, Apps albo nic.
TEMATY_POZA = {'Business Services', 'Home Improvement'}
SLOWA_POZA = ('nieruchomo', 'mieszkan', 'apartament', 'dewelop')


def adres_wyszukiwania(fraza, teraz_ms):
    # query_type=1 przeszukuje tekst reklamy; bez niego biblioteka ignoruje frazę i wypisuje każdą reklamę.
    return (f'{BIBLIOTEKA}/ads?region=PL&start_time={teraz_ms - MIESIAC_MS}&end_time={teraz_ms}'
            f'&adv_name={quote(fraza)}&adv_biz_ids=&query_type=1&sort_type=last_shown_date,desc')


def data(ms):
    """Dzień tak, jak podaje go biblioteka: milisekundy od 1970 o północy UTC."""
    return datetime.fromtimestamp(ms / 1000, timezone.utc).date()


def domena(adres):
    """Host adresu, do którego prowadzi reklama, albo None, gdy reklama go nie podaje."""
    return urlsplit(adres).hostname if adres else None


def w_temacie(reklama):
    """False dla reklamy, która nie sprzedaje produktu finansowego: temat niefinansowy lub słowo z rynku nieruchomości."""
    if reklama.get('subject') in TEMATY_POZA:
        return False
    tekst = f'{reklama.get("title") or ""} {reklama["name"]}'.lower()
    return not any(slowo in tekst for slowo in SLOWA_POZA)


def wybierz(lista):
    """Do NAJWIECEJ reklam na temat i liczba reklam pominiętych jako nie na temat."""
    pasujace = [reklama for reklama in lista if w_temacie(reklama)]
    return pasujace[:NAJWIECEJ], len(lista) - len(pasujace)


def rekord(reklama, szczegoly, zebrano):
    """Rekord z wyniku wyszukiwania i danych szczegółowych reklamy."""
    return {
        'zrodlo': 'tiktok_ads',
        'id_zrodla': reklama['id'],
        'platforma': 'tiktok',
        'url': adres_szczegolow(reklama['id']),
        'domena': domena(szczegoly['ad'].get('external_url')),
        'reklamodawca': reklama['name'],
        'tekst': (reklama.get('title') or '').strip(),
        'zebrano': zebrano,
        'opublikowano': data(reklama['first_shown_date']).isoformat() if reklama.get('first_shown_date') else None,
    }


def adres_szczegolow(id):
    return f'{BIBLIOTEKA}/ads/detail/?ad_id={id}'


def okladka(reklama):
    """Adres obrazu reklamy lub plakatu jej wideo albo None."""
    if reklama.get('image_urls'):
        return reklama['image_urls'][0]
    filmy = reklama.get('videos') or []
    return filmy[0].get('cover_img') if filmy else None


def reklamy(przegladarka, fraza):
    """Zwraca liczbę pasujących reklam, do NAJWIECEJ na temat z danymi szczegółowymi i obrazem, oraz liczbę nie na temat."""
    with przegladarka.new_context(locale='pl-PL', viewport={'width': 1280, 'height': 1400}, **rotacja.ustawienia()) as kontekst:
        karta = kontekst.new_page()
        # Pierwsza wizyta ustawia ciasteczka potrzebne wyszukiwaniu; wyszukiwanie bez nich jest odrzucane.
        karta.goto(f'{BIBLIOTEKA}/ads', wait_until='domcontentloaded', timeout=45000)
        karta.wait_for_timeout(5000)
        with karta.expect_response(lambda odpowiedz: '/api/v1/search' in odpowiedz.url, timeout=45000) as wyszukiwanie:
            karta.goto(adres_wyszukiwania(fraza, int(time.time() * 1000)), wait_until='domcontentloaded', timeout=45000)
        if not wyszukiwanie.value.ok:
            raise RuntimeError(f'wyszukiwanie w bibliotece TikToka odpowiedziało {wyszukiwanie.value.status}')
        wynik = wyszukiwanie.value.json()
        # Biblioteka pomija listę, gdy nic nie pasuje.
        wybrane, poza_tematem = wybierz(wynik.get('data', []))
        znalezione = []
        for reklama in wybrane:
            karta.wait_for_timeout(3000)
            adres = okladka(reklama)
            znalezione.append((reklama, szczegoly(karta, reklama['id']), kontekst.request.get(adres).body() if adres else None))
    return wynik['total'], znalezione, poza_tematem


def szczegoly(karta, id):
    """Dane szczegółowe reklamy, tak jak ładuje je jej strona w bibliotece: adres docelowy i reszta."""
    with karta.expect_response(lambda odpowiedz: f'/api/v1/items/{id}/details' in odpowiedz.url, timeout=45000) as odpowiedz:
        karta.goto(adres_szczegolow(id), wait_until='domcontentloaded', timeout=45000)
    if not odpowiedz.value.ok:
        raise RuntimeError(f'szczegóły reklamy TikTok {id}: odpowiedź {odpowiedz.value.status}')
    return odpowiedz.value.json()['data']


def obsluz(fraza, przegladarka):
    """Szuka jednej frazy i wysyła jej rekordy i obrazy; zwraca dodane, pominięte, błędy (0 lub 1) i linię do wydruku."""
    dodane = obrazy = 0
    try:
        zebrano = datetime.now(timezone.utc).isoformat(timespec='seconds')
        razem, znalezione, poza_tematem = reklamy(przegladarka, fraza)
        for reklama, dane, obraz in znalezione:
            nowy, z_obrazem = wysylka.wyslij(rekord(reklama, dane, zebrano), obraz)
            dodane += nowy
            obrazy += z_obrazem
    except Exception as blad:
        return 0, 0, 1, f'{fraza}: błąd: {type(blad).__name__} {" ".join(str(blad).split())[:200]}'
    pominiete = len(znalezione) - dodane
    return dodane, pominiete, 0, (f'{fraza}: reklamy TikTok: {razem}, poza tematem {poza_tematem}, wzięte {len(znalezione)}; '
                                  f'dodane {dodane}, pominięte {pominiete}; obrazy {obrazy}')


def przeszukaj(frazy):
    from playwright.sync_api import sync_playwright

    dodane = pominiete = bledy = 0
    with sync_playwright() as playwright:
        przegladarka = playwright.chromium.launch(headless=True)
        for fraza in frazy:
            nowe, juz_byly, blad, linia = obsluz(fraza, przegladarka)
            dodane += nowe
            pominiete += juz_byly
            bledy += blad
            print(linia, flush=True)
        przegladarka.close()
    print(f'Podsumowanie: fraz {len(frazy)}, dodane {dodane}, pominięte {pominiete}, błędy {bledy}')


if __name__ == '__main__':
    przeszukaj(sys.argv[1:] or FRAZY)
