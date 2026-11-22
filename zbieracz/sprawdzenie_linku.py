# Link wklejony przez analityka w panelu: otwiera go na komputerze i na telefonie, zachowuje to, co zobaczyła
# przeglądarka, jako dowód, mierzy ostrzeżenie o ryzyku jak strony_docelowe.py i wysyła stronę jako rekord, który
# api ocenia jak reklamę.
import base64
import json
import os
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit

import httpx

import patrol
import siec
import strony_docelowe
import wysylka

# Jak w druga_domena.py: model ocenia teksty długości reklamy, a nie całe strony.
NAJWIECEJ_ZNAKOW = 1500
WEWNETRZNY = 'Link prowadzi do adresu w sieci wewnętrznej, a sprawdzamy tylko strony w internecie.'


def obsluz(zadanie, ostrzezenia, przegladarka, z_cert):
    """Sprawdza jeden link z kolejki i zgłasza do api, jak poszło; zwraca linię do wydruku."""
    zadanie = json.loads(zadanie)
    try:
        zapisz_stan(zadanie['id'], {'stan': 'w_toku'})
        reklama_id, powod = sprawdz(zadanie['url'], ostrzezenia, przegladarka, z_cert)
    except Exception as blad:
        reklama_id, powod = None, 'Nie udało się sprawdzić linku: ' + ' '.join(str(blad).split())[:200]
    if powod:
        zapisz_stan(zadanie['id'], {'stan': 'blad', 'blad': powod})
        return f'{zadanie["url"]}: błąd: {powod}'
    zapisz_stan(zadanie['id'], {'stan': 'gotowe', 'reklama_id': reklama_id})
    return f'{zadanie["url"]}: reklama {reklama_id}'


def sprawdz(url, ostrzezenia, przegladarka, z_cert):
    """Zwraca id rekordu i None albo None i polski powód, dla którego link nie daje rekordu."""
    komputer = odwiedz(przegladarka, url, 'komputer')
    powod = powod_odmowy(komputer)
    if powod:
        return None, powod
    telefon = odwiedz(przegladarka, url, 'telefon')
    rekord_linku = rekord(url, komputer, sygnaly(komputer, ostrzezenia, z_cert))
    # Zapisywane przed rekordem, więc alert o nowym rekordzie już liczy ustalenia o ostrzeżeniu.
    zapisz_pomiar(rekord_linku['domena'], {'komputer': pomiar(komputer), 'telefon': pomiar(telefon)})
    # Robotnik i sprawdzacz pamiętają zapisane rekordy osobno, a rekord linku mógł od tamtej pory zniknąć z bazy.
    wysylka.zapisane.pop((rekord_linku['zrodlo'], rekord_linku['id_zrodla']), None)
    _, zapisany = wysylka.dodaj(rekord_linku)
    for wizyta in (komputer, telefon):
        if 'zrzut' in wizyta:
            wyslij_dowod(zapisany['id'], wizyta)
    if not zapisany['ma_obraz']:
        wysylka.wyslij_obraz(zapisany['id'], komputer['zrzut'])
    return zapisany['id'], None


def odwiedz(przegladarka, url, widok):
    """Co przeglądarka zobaczyła pod linkiem w jednym widoku albo {'blad': powód}, gdy strona się nie otworzyła."""
    from playwright.sync_api import Error

    # Service worker pobierałby zasoby z pominięciem poniższego przechwytywania żądań.
    kontekst = przegladarka.new_context(locale='pl-PL', service_workers='block', **strony_docelowe.WIDOKI[widok])
    kontekst.route('**/*', straz)
    karta = kontekst.new_page()
    lancuch = []

    # Przekierowanie serwera to nowe żądanie głównej ramki, więc te żądania są całym łańcuchem.
    def zapisz_przejscie(zadanie):
        if not zadanie.is_navigation_request():
            return
        try:
            if zadanie.frame is karta.main_frame:
                lancuch.append(zadanie.url)
        except Error:
            pass  # Pierwsze żądanie nowej wewnętrznej ramki przychodzi przed ramką, a ramki wewnętrzne się nie liczą.

    karta.on('request', zapisz_przejscie)
    kiedy = datetime.now(timezone.utc).isoformat(timespec='seconds')
    try:
        odpowiedz = karta.goto(url, wait_until='domcontentloaded', timeout=30000)
        karta.wait_for_timeout(5000)
        # Route widzi tylko pierwszy adres przekierowania serwera, więc cały łańcuch sprawdzany jest tutaj.
        if siec.prowadzi_do_wewnetrznego(lancuch + [karta.url]):
            wizyta = {'blad': WEWNETRZNY}
        else:
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


def straz(trasa):
    """Przepuszcza żądanie strony tylko wtedy, gdy idzie do publicznego internetu."""
    if siec.prowadzi_do_wewnetrznego([trasa.request.url]):
        trasa.abort('blockedbyclient')
    else:
        trasa.continue_()


def powod_bledu(komunikat):
    """Krótki polski powód z błędu przeglądarki; kod net:: odróżnia np. domenę, która nie istnieje."""
    if 'ERR_BLOCKED_BY_CLIENT' in komunikat:
        return WEWNETRZNY
    if 'Timeout' in komunikat:
        return 'Strona nie otworzyła się w ciągu 30 sekund.'
    kod = re.search(r'net::ERR_\w+', komunikat)
    return f'Strona nie otworzyła się ({kod.group()}).' if kod else 'Strona nie otworzyła się.'


def powod_odmowy(wizyta):
    """Polski powód, dla którego wizyta nie może reprezentować strony, albo None, gdy strona się otworzyła."""
    if 'blad' in wizyta:
        return wizyta['blad']
    if wizyta['status'] >= 400:
        return f'Strona odpowiedziała kodem błędu {wizyta["status"]}.'
    if strony_docelowe.WERYFIKACJA.search(wizyta['tytul']):
        return 'Strona zamiast treści pokazała sprawdzenie, czy odwiedza ją człowiek.'
    return None


def pomiar(wizyta):
    """Pomiar ostrzeżenia w jednym widoku tak, jak wysyła go strony_docelowe.py; None, gdy strona się w nim nie otworzyła."""
    return None if powod_odmowy(wizyta) else {'adres': wizyta['adres'], **wizyta['pomiar']}


def wpis_knf(host, ostrzezenia):
    """Wpis listy ostrzeżeń KNF dla hosta lub domeny nadrzędnej albo None."""
    czesci = host.split('.')
    for i in range(len(czesci)):
        if '.'.join(czesci[i:]) in ostrzezenia:
            return ostrzezenia['.'.join(czesci[i:])]
    return None


def sygnaly(wizyta, ostrzezenia, z_cert):
    """Hosty łańcucha przekierowań z listy ostrzeżeń KNF oraz lista CERT Polska dla hosta końcowego."""
    wynik = []
    widziane = set()
    for host in dict.fromkeys(urlsplit(adres).hostname for adres in wizyta['lancuch'] + [wizyta['adres']]):
        wpis = wpis_knf(host, ostrzezenia)
        if wpis and wpis not in widziane:
            widziane.add(wpis)
            wynik.append({'modul': 'M3', 'kod': 'reklama_domeny_z_ostrzezenia_knf',
                          'opis': f'Link prowadzi przez domenę {host}, która jest na liście ostrzeżeń publicznych KNF.',
                          'podstawa': patrol.podstawa_knf(wpis)})
    if z_cert:
        wynik.append(patrol.sygnal_cert(urlsplit(wizyta['adres']).hostname))
    return wynik


def rekord(url, wizyta, sygnaly):
    return {
        'zrodlo': 'panel',
        # Wklejony link jest kluczem, więc drugie jego sprawdzenie dodaje wizyty do tego samego rekordu.
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
