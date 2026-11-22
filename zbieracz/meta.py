# Meta ads (Facebook, Instagram, Messenger) from Ad Library pages an analyst saved in the browser.
# Meta refuses automated visits to the library, so its ads come in only from saved pages or from the official API.
# Usage: python meta.py strona.html [strona.html ...]
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import wysylka

BIBLIOTEKA = 'https://www.facebook.com/ads/library/'
SKRYPT_DANYCH = re.compile(r'<script type="application/json"[^>]*>(.*?)</script>', re.DOTALL)
# A click tracker hides the landing page; the ad's caption names it instead.
SLEDZACE = ('doubleclick.net',)
# A link into Meta's own apps leads to no landing page of the advertiser.
META = ('facebook.com', 'fb.me', 'm.me', 'instagram.com', 'wa.me')


def adres_reklamy(id):
    return f'{BIBLIOTEKA}?id={id}'


def znajdz_reklamy(dane):
    """Every ad in the page's data, at any depth: a dict with an ad_archive_id and a snapshot."""
    if isinstance(dane, dict):
        if 'ad_archive_id' in dane and isinstance(dane.get('snapshot'), dict):
            yield dane
            return
        dane = list(dane.values())
    if isinstance(dane, list):
        for wartosc in dane:
            yield from znajdz_reklamy(wartosc)


def reklamy_ze_strony(html):
    """Ads in the data a saved library page carries, by library id."""
    znalezione = {}
    for dane in SKRYPT_DANYCH.findall(html):
        try:
            wartosc = json.loads(dane)
        except ValueError:
            continue
        for reklama in znajdz_reklamy(wartosc):
            znalezione.setdefault(str(reklama['ad_archive_id']), reklama)
    return znalezione


def data(sekundy):
    """The day from seconds since 1970, as the library gives the first day an ad was shown."""
    return datetime.fromtimestamp(sekundy, timezone.utc).date().isoformat() if sekundy else None


def w_domenie(host, domeny):
    return any(host == domena or host.endswith('.' + domena) for domena in domeny)


def domena(migawka):
    """Host of the advertiser's page the ad leads to, or None when the ad leads to none."""
    host = urlsplit(migawka.get('link_url') or '').hostname
    if host and w_domenie(host, SLEDZACE):
        host = (migawka.get('caption') or '').split('/')[0].lower() or None
    if not host or w_domenie(host, META):
        return None
    return host


def tekst(migawka):
    """The ad's own words; an ad built from cards keeps a placeholder in its body and its words on the first card."""
    tresc = (migawka.get('body') or {}).get('text') or ''
    karty = migawka.get('cards') or []
    if karty and (not tresc or '{{' in tresc):
        tresc = karty[0].get('body') or ''
    return tresc.strip()


def rekord(reklama, zebrano):
    migawka = reklama['snapshot']
    platformy = reklama.get('publisher_platform') or ['facebook']
    return {
        'zrodlo': 'meta_ads',
        'id_zrodla': str(reklama['ad_archive_id']),
        'platforma': platformy[0].lower(),
        'url': adres_reklamy(reklama['ad_archive_id']),
        'domena': domena(migawka),
        'reklamodawca': reklama.get('page_name') or migawka.get('page_name'),
        'tekst': tekst(migawka),
        'zebrano': zebrano,
        'opublikowano': data(reklama.get('start_date')),
    }


def wczytaj(sciezki):
    dodane = pominiete = 0
    for sciezka in map(Path, sciezki):
        # The page shows what the library held when the analyst saved it.
        zebrano = datetime.fromtimestamp(sciezka.stat().st_mtime, timezone.utc).isoformat(timespec='seconds')
        reklamy = reklamy_ze_strony(sciezka.read_text(encoding='utf-8', errors='replace'))
        nowe = sum(wysylka.dodaj(rekord(reklama, zebrano))[0] for reklama in reklamy.values())
        dodane += nowe
        pominiete += len(reklamy) - nowe
        print(f'{sciezka.name}: reklamy Mety {len(reklamy)}, dodane {nowe}, pominięte {len(reklamy) - nowe}', flush=True)
    print(f'Podsumowanie: stron {len(sciezki)}, dodane {dodane}, pominięte {pominiete}')


if __name__ == '__main__':
    wczytaj(sys.argv[1:])
