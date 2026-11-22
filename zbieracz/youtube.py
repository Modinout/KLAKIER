# Filmy z publicznego kanału RSS kanałów YouTube, wysyłane do api; nie jest uruchamiany przez harmonogram.
# Użycie: python youtube.py <id_kanalu> [<id_kanalu> ...]
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import httpx

import wysylka

FEED = 'https://www.youtube.com/feeds/videos.xml?channel_id='
NS = {'a': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015',
      'm': 'http://search.yahoo.com/mrss/'}


def rekordy(xml, zebrano):
    """Rekordy z wpisów kanału RSS."""
    wynik = []
    for wpis in ET.fromstring(xml).findall('a:entry', NS):
        id = wpis.findtext('yt:videoId', namespaces=NS)
        tytul = wpis.findtext('a:title', default='', namespaces=NS)
        opis = wpis.findtext('m:group/m:description', default='', namespaces=NS)
        wynik.append({
            'zrodlo': 'youtube',
            'id_zrodla': id,
            'platforma': 'youtube',
            'url': f'https://www.youtube.com/watch?v={id}',
            'domena': None,
            'reklamodawca': wpis.findtext('a:author/a:name', default='', namespaces=NS),
            'tekst': f'{tytul}\n{opis}',
            'zebrano': zebrano,
            'opublikowano': wpis.findtext('a:published', default='', namespaces=NS)[:10] or None,
        })
    return wynik


def kanal(id):
    odpowiedz = httpx.get(FEED + id, timeout=30)
    odpowiedz.raise_for_status()
    return rekordy(odpowiedz.content, datetime.now(timezone.utc).isoformat(timespec='seconds'))


def wyslij(lista):
    """Wysyła rekordy; zwraca liczbę nowych."""
    return sum(wysylka.dodaj(rekord)[0] for rekord in lista)


if __name__ == '__main__':
    for id in sys.argv[1:]:
        lista = kanal(id)
        print(f'{id}: wpisy {len(lista)}, nowe {wyslij(lista)}')
