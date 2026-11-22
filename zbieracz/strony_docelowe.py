# Mierzy ostrzeżenie o ryzyku na stronach głównych, do których prowadzą reklamy firm z rejestru KNF, na komputerze,
# tablecie i telefonie, i wysyła każdy pomiar do api, które zamienia go w ustalenia przy każdym odczycie.
# Użycie: python strony_docelowe.py [domena ...]; bez domen bierze domeny docelowe tych reklam.
import os
import re
import sys
from pathlib import Path

import httpx

import rotacja

POMIAR = Path(__file__).with_name('pomiar_ostrzezenia.js').read_text(encoding='utf-8')
WIDOKI = {
    'komputer': {'viewport': {'width': 1366, 'height': 900}},
    'tablet': {'viewport': {'width': 768, 'height': 1024}, 'is_mobile': True, 'has_touch': True},
    # Wąskie okno z własnym User-Agentem przeglądarki, żeby strona pokazała układ, który daje telefonom według szerokości.
    'telefon': {'viewport': {'width': 390, 'height': 844}, 'is_mobile': True, 'has_touch': True},
}
STANY_Z_REJESTRU = {'w_rejestrze', 'spoza_rejestru'}
WERYFIKACJA = re.compile(r'just a moment|attention required|access denied|verify you are human|captcha', re.I)


def domeny_z_rejestru():
    reklamy = httpx.get(f"{os.environ['API_URL']}/reklamy", timeout=120).raise_for_status().json()
    return sorted({reklama['domena'] for reklama in reklamy
                   if reklama['domena'] and reklama['rejestr'] and reklama['rejestr']['stan'] in STANY_Z_REJESTRU})


def zmierz(przegladarka, domena, widok):
    """Pomiar strony głównej w jednym widoku albo None, gdy się nie otwiera lub pokazuje sprawdzenie botów."""
    from playwright.sync_api import Error

    kontekst = przegladarka.new_context(locale='pl-PL', **WIDOKI[widok], **rotacja.ustawienia())
    karta = kontekst.new_page()
    try:
        odpowiedz = karta.goto(f'https://{domena}/', wait_until='domcontentloaded', timeout=30000)
        karta.wait_for_timeout(5000)
        if odpowiedz is None or odpowiedz.status >= 400 or WERYFIKACJA.search(karta.title()):
            pomiar = None
        else:
            pomiar = {'adres': karta.url, **karta.evaluate(POMIAR)}
    except Error as blad:
        print(f'{domena} ({widok}): {" ".join(blad.message.split())[:150]}')
        pomiar = None
    kontekst.close()
    return pomiar


def opis(pomiar):
    if pomiar is None:
        return 'nie otworzyła się'
    ostrzezenie = pomiar['ostrzezenie']
    if ostrzezenie is None:
        return 'brak ostrzeżenia' + (', jest mowa o CFD' if pomiar['cfd'] else '')
    return (f'ostrzeżenie {ostrzezenie["px"]} px przy {pomiar["przewazajacy_px"]} px, kontrast {ostrzezenie["kontrast"]}, '
            f'widoczne {ostrzezenie["widoczne"]}, bez przewijania {ostrzezenie["bez_przewijania"]}')


def obsluz(przegladarka, domena):
    """Mierzy jedną domenę i wysyła pomiar; zwraca, czy zmierzono, i linię do wydruku."""
    komputer = zmierz(przegladarka, domena, 'komputer')
    if komputer is None:
        # Strona, która odmówiła przy pierwszej wizycie, nie jest pytana ponownie.
        return False, f'{domena}: strona nie otworzyła się albo odmówiła, pomijam'
    tablet = zmierz(przegladarka, domena, 'tablet')
    telefon = zmierz(przegladarka, domena, 'telefon')
    httpx.put(f"{os.environ['API_URL']}/strony/{domena}", json={'komputer': komputer, 'tablet': tablet, 'telefon': telefon},
              timeout=30).raise_for_status()
    return True, f'{domena}: komputer: {opis(komputer)}; tablet: {opis(tablet)}; telefon: {opis(telefon)}'


def zmierz_wszystkie(domeny):
    from playwright.sync_api import sync_playwright

    zmierzone = 0
    with sync_playwright() as playwright:
        przegladarka = playwright.chromium.launch(headless=True)
        for domena in domeny:
            try:
                zmierzona, linia = obsluz(przegladarka, domena)
            except httpx.HTTPError as blad:
                zmierzona, linia = False, f'{domena}: api nie przyjęło pomiaru: {blad}'
            zmierzone += zmierzona
            print(linia, flush=True)
        przegladarka.close()
    print(f'Podsumowanie: domen {len(domeny)}, zmierzone {zmierzone}, pominięte {len(domeny) - zmierzone}')


if __name__ == '__main__':
    zmierz_wszystkie(sys.argv[1:] or domeny_z_rejestru())
