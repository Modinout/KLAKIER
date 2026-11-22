# A link an analyst pasted in the panel: opens it on a computer and on a phone, keeps what the browser saw as
# evidence, measures the risk warning like strony_docelowe.py and sends the page as a record the api scores like an ad.
import base64
import json
import os
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit

import httpx

import patrol
import strony_docelowe
import wysylka

# As druga_domena.py: the model judges texts the length of an ad, not whole pages.
NAJWIECEJ_ZNAKOW = 1500


def obsluz(zadanie, ostrzezenia, przegladarka, z_cert):
    """Checks one link from the queue and reports to the api how it went; returns the line to print."""
    zadanie = json.loads(zadanie)
    zapisz_stan(zadanie['id'], {'stan': 'w_toku'})
    try:
        reklama_id, powod = sprawdz(zadanie['url'], ostrzezenia, przegladarka, z_cert)
    except Exception as blad:
        reklama_id, powod = None, 'Nie udało się sprawdzić linku: ' + ' '.join(str(blad).split())[:200]
    if powod:
        zapisz_stan(zadanie['id'], {'stan': 'blad', 'blad': powod})
        return f'{zadanie["url"]}: błąd: {powod}'
    zapisz_stan(zadanie['id'], {'stan': 'gotowe', 'reklama_id': reklama_id})
    return f'{zadanie["url"]}: reklama {reklama_id}'


def sprawdz(url, ostrzezenia, przegladarka, z_cert):
    """Returns the id of the record and None, or None and the Polish reason why the link gives no record."""
    komputer = odwiedz(przegladarka, url, 'komputer')
    powod = powod_odmowy(komputer)
    if powod:
        return None, powod
    telefon = odwiedz(przegladarka, url, 'telefon')
    rekord_linku = rekord(url, komputer, sygnaly(komputer, ostrzezenia, z_cert))
    # Stored before the record, so the alert for the new record already counts the findings about the warning.
    zapisz_pomiar(rekord_linku['domena'], {'komputer': pomiar(komputer), 'telefon': pomiar(telefon)})
    _, zapisany = wysylka.dodaj(rekord_linku)
    for wizyta in (komputer, telefon):
        if 'zrzut' in wizyta:
            wyslij_dowod(zapisany['id'], wizyta)
    if not zapisany['ma_obraz']:
        wysylka.wyslij_obraz(zapisany['id'], komputer['zrzut'])
    return zapisany['id'], None


def odwiedz(przegladarka, url, widok):
    """What the browser saw on the link in one view, or {'blad': reason} when the page did not open."""
    from playwright.sync_api import Error

    kontekst = przegladarka.new_context(locale='pl-PL', **strony_docelowe.WIDOKI[widok])
    karta = kontekst.new_page()
    lancuch = []

    # A server redirect is a new request of the main frame, so these requests are the whole chain.
    def zapisz_przejscie(zadanie):
        if not zadanie.is_navigation_request():
            return
        try:
            if zadanie.frame is karta.main_frame:
                lancuch.append(zadanie.url)
        except Error:
            pass  # The first request of a new inner frame comes before the frame, and inner frames do not count.

    karta.on('request', zapisz_przejscie)
    kiedy = datetime.now(timezone.utc).isoformat(timespec='seconds')
    try:
        odpowiedz = karta.goto(url, wait_until='domcontentloaded', timeout=30000)
        karta.wait_for_timeout(5000)
        wizyta = {
            'kiedy': kiedy, 'rodzaj': widok, 'status': odpowiedz.status, 'adres': karta.url, 'lancuch': lancuch,
            'tytul': karta.title().strip(),
            'tekst': ' '.join(karta.evaluate('document.body.innerText').split()),
            'pomiar': karta.evaluate(strony_docelowe.POMIAR),
            'html': karta.content(),
            'zrzut': karta.screenshot(full_page=True),
        }
    except Error as blad:
        wizyta = {'blad': powod_bledu(blad.message)}
    kontekst.close()
    return wizyta


def powod_bledu(komunikat):
    """Short Polish reason from a browser error; the net:: code tells apart e.g. a domain that does not exist."""
    if 'Timeout' in komunikat:
        return 'Strona nie otworzyła się w ciągu 30 sekund.'
    kod = re.search(r'net::ERR_\w+', komunikat)
    return f'Strona nie otworzyła się ({kod.group()}).' if kod else 'Strona nie otworzyła się.'


def powod_odmowy(wizyta):
    """Polish reason why the visit cannot stand for the page, or None when the page opened."""
    if 'blad' in wizyta:
        return wizyta['blad']
    if wizyta['status'] >= 400:
        return f'Strona odpowiedziała kodem błędu {wizyta["status"]}.'
    if strony_docelowe.WERYFIKACJA.search(wizyta['tytul']):
        return 'Strona zamiast treści pokazała sprawdzenie, czy odwiedza ją człowiek.'
    return None


def pomiar(wizyta):
    """The warning measurement of one view as strony_docelowe.py sends it; None when the page did not open in it."""
    return None if powod_odmowy(wizyta) else {'adres': wizyta['adres'], **wizyta['pomiar']}


def wpis_knf(host, ostrzezenia):
    """Entry of the KNF warning list for the host or a domain above it, or None."""
    czesci = host.split('.')
    for i in range(len(czesci)):
        if '.'.join(czesci[i:]) in ostrzezenia:
            return ostrzezenia['.'.join(czesci[i:])]
    return None


def sygnaly(wizyta, ostrzezenia, z_cert):
    """Hosts of the redirect chain on the KNF warning list, and the CERT Polska list for the final host."""
    wynik = []
    for host in dict.fromkeys(urlsplit(adres).hostname for adres in wizyta['lancuch'] + [wizyta['adres']]):
        wpis = wpis_knf(host, ostrzezenia)
        if wpis:
            wynik.append({'modul': 'M3', 'kod': 'reklama_domeny_z_ostrzezenia_knf',
                          'opis': f'Link prowadzi przez domenę {host}, która jest na liście ostrzeżeń publicznych KNF.',
                          'podstawa': patrol.podstawa_knf(wpis)})
    if z_cert:
        wynik.append(patrol.sygnal_cert(urlsplit(wizyta['adres']).hostname))
    return wynik


def rekord(url, wizyta, sygnaly):
    return {
        'zrodlo': 'panel',
        # The pasted link is the key, so a second check of it adds its visits to the same record.
        'id_zrodla': url,
        'platforma': 'www',
        'url': url,
        'domena': urlsplit(wizyta['adres']).hostname,
        'reklamodawca': None,
        'tekst': f'{wizyta["tytul"]} {wizyta["tekst"][:NAJWIECEJ_ZNAKOW]}'.strip(),
        'zebrano': wizyta['kiedy'],
        'opublikowano': None,
        'sygnaly': sygnaly,
    }


def zapisz_stan(id, stan):
    httpx.put(f"{os.environ['API_URL']}/sprawdz/{id}", json=stan, timeout=30).raise_for_status()


def zapisz_pomiar(domena, widoki):
    httpx.put(f"{os.environ['API_URL']}/strony/{domena}", json=widoki, timeout=30).raise_for_status()


def wyslij_dowod(reklama_id, wizyta):
    dowod = {pole: wizyta[pole] for pole in ('kiedy', 'rodzaj', 'adres', 'lancuch', 'html')}
    httpx.post(f"{os.environ['API_URL']}/reklamy/{reklama_id}/dowody",
               json={**dowod, 'obraz': base64.b64encode(wizyta['zrzut']).decode()}, timeout=120).raise_for_status()
