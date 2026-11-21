# TikTok ads shown in Poland that match a phrase, read from TikTok's public commercial content library.
# Usage: python tiktok.py [fraza ...]; with no phrases it searches a short list of investment phrases.
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
# A deny-list, because TikTok's topic label is unreliable: the same ad gets Financial Services, Apps or nothing.
TEMATY_POZA = {'Business Services', 'Home Improvement'}
SLOWA_POZA = ('nieruchomo', 'mieszkan', 'apartament', 'dewelop')


def adres_wyszukiwania(fraza, teraz_ms):
    # query_type=1 searches the ad text; without it the library ignores the phrase and lists every ad.
    return (f'{BIBLIOTEKA}/ads?region=PL&start_time={teraz_ms - MIESIAC_MS}&end_time={teraz_ms}'
            f'&adv_name={quote(fraza)}&adv_biz_ids=&query_type=1&sort_type=last_shown_date,desc')


def data(ms):
    """A day as the library gives it: milliseconds since 1970 at midnight UTC."""
    return datetime.fromtimestamp(ms / 1000, timezone.utc).date()


def domena(adres):
    """Host of the address the ad leads to, or None when the ad gives none."""
    return urlsplit(adres).hostname if adres else None


def w_temacie(reklama):
    """False for an ad that sells no financial product: a non-financial topic or a real-estate word."""
    if reklama.get('subject') in TEMATY_POZA:
        return False
    tekst = f'{reklama.get("title") or ""} {reklama["name"]}'.lower()
    return not any(slowo in tekst for slowo in SLOWA_POZA)


def wybierz(lista):
    """Up to NAJWIECEJ ads on topic and the number of ads left out as off topic."""
    pasujace = [reklama for reklama in lista if w_temacie(reklama)]
    return pasujace[:NAJWIECEJ], len(lista) - len(pasujace)


def rekord(reklama, szczegoly, zebrano):
    """Record from a search result and the ad's detail data."""
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
    """Address of the ad's picture or of its video poster, or None."""
    if reklama.get('image_urls'):
        return reklama['image_urls'][0]
    filmy = reklama.get('videos') or []
    return filmy[0].get('cover_img') if filmy else None


def reklamy(przegladarka, fraza):
    """Returns the number of matching ads, up to NAJWIECEJ on topic with detail data and picture, and the number off topic."""
    with przegladarka.new_context(locale='pl-PL', viewport={'width': 1280, 'height': 1400}, **rotacja.ustawienia()) as kontekst:
        karta = kontekst.new_page()
        # The first visit sets the cookies the search needs; a search without them is refused.
        karta.goto(f'{BIBLIOTEKA}/ads', wait_until='domcontentloaded', timeout=45000)
        karta.wait_for_timeout(5000)
        with karta.expect_response(lambda odpowiedz: '/api/v1/search' in odpowiedz.url, timeout=45000) as wyszukiwanie:
            karta.goto(adres_wyszukiwania(fraza, int(time.time() * 1000)), wait_until='domcontentloaded', timeout=45000)
        if not wyszukiwanie.value.ok:
            raise RuntimeError(f'wyszukiwanie w bibliotece TikToka odpowiedziało {wyszukiwanie.value.status}')
        wynik = wyszukiwanie.value.json()
        # The library leaves out the list when nothing matches.
        wybrane, poza_tematem = wybierz(wynik.get('data', []))
        znalezione = []
        for reklama in wybrane:
            karta.wait_for_timeout(3000)
            adres = okladka(reklama)
            znalezione.append((reklama, szczegoly(karta, reklama['id']), kontekst.request.get(adres).body() if adres else None))
    return wynik['total'], znalezione, poza_tematem


def szczegoly(karta, id):
    """The ad's detail data, as its library page loads it: landing address and the rest."""
    with karta.expect_response(lambda odpowiedz: f'/api/v1/items/{id}/details' in odpowiedz.url, timeout=45000) as odpowiedz:
        karta.goto(adres_szczegolow(id), wait_until='domcontentloaded', timeout=45000)
    if not odpowiedz.value.ok:
        raise RuntimeError(f'szczegóły reklamy TikTok {id}: odpowiedź {odpowiedz.value.status}')
    return odpowiedz.value.json()['data']


def obsluz(fraza, przegladarka):
    """Searches one phrase and sends its records and pictures; returns added, skipped, errors (0 or 1) and the line to print."""
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
