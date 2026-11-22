# Tytuł sprawy tak, jak buduje go panel w front/src/sprawy.js, żeby api nazywało sprawę tak samo.
import re
from urllib.parse import urlsplit

BIBLIOTEKI = ('adstransparency.google.com', 'library.tiktok.com')
# Jedna wielkość liter w końcówce, żeby "dywidendy.Skorzystaj" nie zostało wzięte za domenę.
DOMENA = re.compile(r'\b(?:[A-Za-z0-9-]+\.)+(?:[a-z]{2,}|[A-Z]{2,})\b', re.ASCII)


def tytul(reklama):
    """reklama: wiersz tabeli reklamy."""
    return (ostrzezona_domena(reklama) or reklama['reklamodawca'] or domena_docelowa(reklama)
            or pierwsza_domena(reklama['tekst']) or 'Reklama bez nadawcy')


def ostrzezona_domena(reklama):
    for sygnal in reklama['sygnaly_zbieracza'] + reklama['sygnaly']:
        if sygnal['kod'] == 'reklama_domeny_z_ostrzezenia_knf':
            return domena_docelowa(reklama) or pierwsza_domena(sygnal['opis'])
    return None


def domena_docelowa(reklama):
    if reklama['domena']:
        return reklama['domena'].removeprefix('www.')
    # Strona biblioteki reklam pokazuje samą reklamę, a nie to, dokąd prowadzi.
    if reklama['url'] and not z_biblioteki(reklama['url']):
        return domena(reklama['url'])
    return None


def domena(url):
    host = urlsplit(url).hostname
    return host.removeprefix('www.') if host else url


def z_biblioteki(url):
    return domena(url) in BIBLIOTEKI or 'facebook.com/ads/library' in url


def pierwsza_domena(tekst):
    znaleziona = DOMENA.search(tekst)
    return znaleziona and re.sub(r'^www\.', '', znaleziona[0], flags=re.IGNORECASE).lower()
