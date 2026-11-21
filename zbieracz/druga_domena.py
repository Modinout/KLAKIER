# Finds a second domain that runs the same site as a warned domain.
import hashlib
import re
from collections import Counter
from urllib.parse import urljoin, urlsplit

import rotacja

IDENTYFIKATORY = [
    re.compile(r'\b(GTM-[A-Z0-9]{5,9})\b'),
    re.compile(r'\b(G-[A-Z0-9]{8,12})\b'),
    re.compile(r'\b(AW-\d{8,})\b'),
    re.compile(r'''fbq\(\s*['"]init['"]\s*,\s*['"](\d{8,})'''),
    re.compile(r'facebook\.com/tr/?\?id=(\d{8,})'),
]
DWUCZLONOWE = {'co.uk', 'com.pl', 'net.pl', 'org.pl', 'edu.pl', 'com.au', 'co.za', 'com.cy', 'com.ua',
               'co.nz', 'com.br', 'com.tr', 'co.il', 'com.mt', 'com.hk', 'com.sg', 'co.in'}
POMIJANE = {
    'facebook.com', 'instagram.com', 'twitter.com', 'x.com', 'linkedin.com', 'youtube.com', 'youtu.be',
    'tiktok.com', 't.me', 'telegram.org', 'telegram.me', 'whatsapp.com', 'wa.me', 'pinterest.com', 'vk.com',
    'reddit.com', 'google.com', 'apple.com', 'microsoft.com',
    'gov.pl', 'knf.gov.pl', 'gov.cy', 'org.uk', 'europa.eu', 'gov.au', 'sec.gov', 'finra.org', 'bafin.de',
}
SLOWA_OFERTY = ['forex', 'cfd', 'broker', 'trading', 'trader', 'inwest', 'invest', 'akcje', 'obligacj',
                'kryptowalut', 'crypto', 'bitcoin', 'kontrakt', 'dźwigni', 'leverage', 'portfel', 'depozyt',
                'rynk', 'giełd']
NAJMNIEJ_LINKOW = 5
NAJWIECEJ_KANDYDATOW = 3
SZKIELET = 'body > *, body > * > *, body > * > * > *'


def znajdz(przegladarka, domena, ostrzezone):
    """Returns the second domain with its matching traces, title, text and screenshot, or None."""
    ostrzezona = odwiedz(przegladarka, domena)
    if not ostrzezona:
        return None
    for kandydat in kandydaci(ostrzezona['linki'], domena, ostrzezone):
        strona = odwiedz(przegladarka, kandydat)
        # An expired warned domain often redirects to an unrelated site, which then matches itself.
        if strona and ta_sama_strona(ostrzezona, strona) and wyglada_na_oferte(strona['tekst']):
            return {'domena': kandydat, 'zgodne': ['tytuł'] + zgodne_slady(ostrzezona, strona),
                    'tytul': strona['tytul'], 'tekst': strona['tekst'][:1500], 'obraz': strona['zrzut']}
    return None


def odwiedz(przegladarka, domena):
    """Traces, links, visible text and screenshot of a home page, or None when the site does not open."""
    from playwright.sync_api import Error

    kontekst = przegladarka.new_context(locale='pl-PL', viewport={'width': 1366, 'height': 900}, **rotacja.ustawienia())
    karta = kontekst.new_page()
    zadania = []
    karta.on('request', lambda zadanie: zadania.append(zadanie.url))
    try:
        karta.goto(f'https://{domena}', wait_until='domcontentloaded', timeout=30000)
        karta.wait_for_timeout(6000)
        html = karta.content()
        strona = {
            'tytul': karta.title().strip(),
            'favicon': favicon(kontekst, karta),
            'szkielet': skrot(','.join(karta.eval_on_selector_all(SZKIELET, 'el => el.map(e => e.tagName)'))),
            'identyfikatory': identyfikatory(html + '\n' + '\n'.join(zadania)),
            'linki': karta.eval_on_selector_all('a[href]', 'el => el.map(a => a.href)'),
            'tekst': ' '.join(karta.evaluate('document.body.innerText').split()),
            'zrzut': karta.screenshot(),
        }
    except Error:
        strona = None
    kontekst.close()
    return strona


def favicon(kontekst, karta):
    from playwright.sync_api import Error

    adres = karta.evaluate('(document.querySelector(\'link[rel~="icon"]\') || {}).href || "/favicon.ico"')
    try:
        odpowiedz = kontekst.request.get(urljoin(karta.url, adres), timeout=15000)
        dane = odpowiedz.body()
    except Error:
        return ''
    return f'{skrot(dane)}:{len(dane)}' if odpowiedz.ok and dane else ''


def skrot(dane):
    if not dane:
        return ''
    return hashlib.md5(dane.encode() if isinstance(dane, str) else dane).hexdigest()[:12]


def identyfikatory(tekst):
    return {znalezione for wzor in IDENTYFIKATORY for znalezione in wzor.findall(tekst)}


def rejestrowa(host):
    czesci = host.lower().removeprefix('www.').split('.')
    ile = 3 if '.'.join(czesci[-2:]) in DWUCZLONOWE else 2
    return '.'.join(czesci[-ile:])


def kandydaci(linki, domena, ostrzezone):
    """External domains linked often enough from the warned home page, most linked first."""
    licznik = Counter()
    for link in linki:
        host = urlsplit(link).hostname
        if host and '.' in host:
            licznik[rejestrowa(host)] += 1
    return [kandydat for kandydat, ile in licznik.most_common()
            if ile >= NAJMNIEJ_LINKOW and kandydat != domena
            and kandydat not in POMIJANE and kandydat not in ostrzezone][:NAJWIECEJ_KANDYDATOW]


def zgodne_slady(a, b):
    """Matching traces besides the title, one Polish phrase per kind of trace."""
    zgodne = []
    if a['favicon'] and a['favicon'] == b['favicon']:
        zgodne.append('ikona strony')
    if a['szkielet'] and a['szkielet'] == b['szkielet']:
        zgodne.append('układ strony')
    wspolne = sorted(a['identyfikatory'] & b['identyfikatory'])
    if len(wspolne) == 1:
        zgodne.append(f'identyfikator śledzący {wspolne[0]}')
    elif wspolne:
        zgodne.append('identyfikatory śledzące ' + ', '.join(wspolne))
    return zgodne


def wyglada_na_oferte(tekst):
    tekst = tekst.lower()
    return sum(slowo in tekst for slowo in SLOWA_OFERTY) >= 2


def ta_sama_strona(a, b):
    return bool(a['tytul']) and a['tytul'] == b['tytul'] and len(zgodne_slady(a, b)) >= 2
