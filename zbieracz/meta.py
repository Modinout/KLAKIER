# Reklamy Mety (Facebook, Instagram, Messenger) ze stron biblioteki reklam zapisanych przez analityka w przeglądarce.
# Meta odmawia zautomatyzowanych wizyt w bibliotece, więc jej reklamy trafiają tylko z zapisanych stron
# lub z oficjalnego API.
# Użycie: python meta.py strona.html [strona.html ...]
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import wysylka

BIBLIOTEKA = 'https://www.facebook.com/ads/library/'
SKRYPT_DANYCH = re.compile(r'<script type="application/json"[^>]*>(.*?)</script>', re.DOTALL)
# Tracker kliknięć ukrywa stronę docelową; nazywa ją za to podpis reklamy.
SLEDZACE = ('doubleclick.net',)
# Link do własnych aplikacji Mety nie prowadzi do żadnej strony docelowej reklamodawcy.
META = ('facebook.com', 'fb.me', 'm.me', 'instagram.com', 'wa.me')


def adres_reklamy(id):
    return f'{BIBLIOTEKA}?id={id}'


def znajdz_reklamy(dane):
    """Każda reklama w danych strony, na dowolnej głębokości: słownik z ad_archive_id i snapshot."""
    if isinstance(dane, dict):
        if 'ad_archive_id' in dane and isinstance(dane.get('snapshot'), dict):
            yield dane
            return
        dane = list(dane.values())
    if isinstance(dane, list):
        for wartosc in dane:
            yield from znajdz_reklamy(wartosc)


def reklamy_ze_strony(html):
    """Reklamy w danych zapisanej strony biblioteki, według id biblioteki."""
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
    """Dzień z sekund od 1970, tak jak biblioteka podaje pierwszy dzień wyświetlania reklamy."""
    return datetime.fromtimestamp(sekundy, timezone.utc).date().isoformat() if sekundy else None


def w_domenie(host, domeny):
    return any(host == domena or host.endswith('.' + domena) for domena in domeny)


def domena(migawka):
    """Host strony reklamodawcy, do której prowadzi reklama, albo None, gdy nie prowadzi do żadnej."""
    host = urlsplit(migawka.get('link_url') or '').hostname
    if host and w_domenie(host, SLEDZACE):
        host = (migawka.get('caption') or '').split('/')[0].lower() or None
    if not host or w_domenie(host, META):
        return None
    return host


def tekst(migawka):
    """Własne słowa reklamy; reklama zbudowana z kart trzyma w treści wypełniacz, a swoje słowa na pierwszej karcie."""
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
        # Strona pokazuje to, co biblioteka zawierała w chwili zapisu przez analityka.
        zebrano = datetime.fromtimestamp(sciezka.stat().st_mtime, timezone.utc).isoformat(timespec='seconds')
        reklamy = reklamy_ze_strony(sciezka.read_text(encoding='utf-8', errors='replace'))
        nowe = sum(wysylka.dodaj(rekord(reklama, zebrano))[0] for reklama in reklamy.values())
        dodane += nowe
        pominiete += len(reklamy) - nowe
        print(f'{sciezka.name}: reklamy Mety {len(reklamy)}, dodane {nowe}, pominięte {len(reklamy) - nowe}', flush=True)
    print(f'Podsumowanie: stron {len(sciezki)}, dodane {dodane}, pominięte {pominiete}')


if __name__ == '__main__':
    wczytaj(sys.argv[1:])
