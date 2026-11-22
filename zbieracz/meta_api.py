# Meta ads that match a phrase, read from Meta's official Ad Library API.
# Needs META_TOKEN in the environment; without it nothing is requested.
# Usage: python meta_api.py
import os
import sys
from datetime import datetime, timedelta, timezone

import httpx

import meta
import wysylka

ADRES = 'https://graph.facebook.com/v27.0/ads_archive'
FRAZY = ['inwestowanie', 'forex', 'kryptowaluty', 'giełda', 'trading']
NAJWIECEJ_STRON = 10
DNI_WSTECZ = 2
POLA = ','.join(['id', 'page_name', 'publisher_platforms', 'ad_delivery_start_time', 'ad_creative_bodies',
                 'ad_creative_link_titles', 'ad_creative_link_captions'])


class BladApi(Exception):
    pass


def strony(token, fraza):
    """Pages of ads that match the phrase, following the paging link."""
    # The window starts before the last run, so a short-lived ad that already stopped is still caught.
    od = (datetime.now(timezone.utc) - timedelta(days=DNI_WSTECZ)).date().isoformat()
    adres = ADRES
    parametry = {'access_token': token, 'ad_reached_countries': "['PL']", 'ad_type': 'ALL', 'ad_active_status': 'ALL',
                 'ad_delivery_date_min': od, 'search_terms': fraza, 'fields': POLA}
    for _ in range(NAJWIECEJ_STRON):
        wynik = httpx.get(adres, params=parametry, timeout=60).json()
        if 'error' in wynik:
            raise BladApi(f'{wynik["error"].get("code")} {wynik["error"].get("message")}')
        if not wynik.get('data'):
            return
        yield wynik['data']
        # The link already carries every parameter.
        adres, parametry = wynik.get('paging', {}).get('next'), None
        if not adres:
            return


def pierwszy(reklama, pole):
    lista = reklama.get(pole) or []
    return lista[0] if lista else None


def domena(reklama):
    # A caption can be a button or form text, and a shared fake domain would join unrelated payers.
    host = (pierwszy(reklama, 'ad_creative_link_captions') or '').split('/')[0].strip().lower()
    if '.' not in host or ' ' in host or meta.w_domenie(host, meta.META):
        return None
    return host


def tekst(reklama):
    """The ad's own words; a body that is only a template placeholder gives way to the link title."""
    tresc = pierwszy(reklama, 'ad_creative_bodies') or ''
    tytul = pierwszy(reklama, 'ad_creative_link_titles')
    if tytul and (not tresc or '{{' in tresc):
        tresc = tytul
    return tresc.strip()


def rekord(reklama, zebrano):
    return {
        'zrodlo': 'meta_ads',
        'id_zrodla': str(reklama['id']),
        'platforma': (reklama.get('publisher_platforms') or ['FACEBOOK'])[0].lower(),
        'url': meta.adres_reklamy(reklama['id']),
        'domena': domena(reklama),
        'reklamodawca': reklama.get('page_name'),
        'tekst': tekst(reklama),
        'zebrano': zebrano,
        'opublikowano': (reklama.get('ad_delivery_start_time') or '')[:10] or None,
    }


def obsluz(token, fraza, widziane, zebrano):
    """Searches one phrase and sends its ads not seen under an earlier phrase; returns found and added."""
    znalezione = dodane = 0
    for strona in strony(token, fraza):
        for reklama in strona:
            znalezione += 1
            if reklama['id'] in widziane:
                continue
            widziane.add(reklama['id'])
            dodane += wysylka.dodaj(rekord(reklama, zebrano))[0]
    return znalezione, dodane


def przeszukaj():
    token = os.environ.get('META_TOKEN')
    if not token:
        print('Brak META_TOKEN: pomijam reklamy Mety z API.')
        return 0
    zebrano = datetime.now(timezone.utc).isoformat(timespec='seconds')
    widziane = set()
    razem = dodane = 0
    try:
        for fraza in FRAZY:
            znalezione, nowe = obsluz(token, fraza, widziane, zebrano)
            razem += znalezione
            dodane += nowe
            print(f'{fraza}: reklamy Mety {znalezione}, dodane {nowe}', flush=True)
    except BladApi as blad:
        print(f'Błąd API Mety: {blad}')
        return 1
    print(f'Podsumowanie: fraz {len(FRAZY)}, reklam {razem}, dodane {dodane}, pominięte {razem - dodane}')
    return 0


if __name__ == '__main__':
    sys.exit(przeszukaj())
