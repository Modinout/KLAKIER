# The case title as the panel builds it in front/src/sprawy.js, so that the api names a case the same way.
import re
from urllib.parse import urlsplit

BIBLIOTEKI = ('adstransparency.google.com', 'library.tiktok.com')
# One case of letters in the ending, so "dywidendy.Skorzystaj" is not taken for a domain.
DOMENA = re.compile(r'\b(?:[A-Za-z0-9-]+\.)+(?:[a-z]{2,}|[A-Z]{2,})\b', re.ASCII)


def tytul(reklama):
    """reklama: a row of the reklamy table."""
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
    # An ad library page shows the ad itself, not where the ad leads.
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
