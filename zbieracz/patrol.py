# Checks domains from the KNF public warning list and sends what it finds to the api.
# Usage: python patrol.py [domena ...]; with no domains it checks the whole list.
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

import druga_domena
import lista_cert
import reklamy_google
import wysylka

OSTRZEZENIA = Path(__file__).with_name('ostrzezenia_knf.csv')


def wczytaj_ostrzezenia():
    with open(OSTRZEZENIA, encoding='utf-8', newline='') as plik:
        return {wiersz['domena']: wiersz['wpis'] for wiersz in csv.DictReader(plik, delimiter=';')}


def podstawa_knf(wpis):
    return f'Lista ostrzeżeń publicznych KNF: {wpis}'


def rekord_reklamy(domena, wpis, reklama, zebrano):
    return {
        'zrodlo': 'google_ads',
        'id_zrodla': reklama['kreacja'],
        'platforma': 'google',
        'url': f'https://{domena}/',
        'domena': domena,
        'reklamodawca': reklama['reklamodawca'],
        # Google draws the ad as a picture; the api reads the text from it when the picture arrives.
        'tekst': '',
        'zebrano': zebrano,
        'opublikowano': reklama['pierwsza'].isoformat(),
        'sygnaly': [{
            'modul': 'M3',
            'kod': 'reklama_domeny_z_ostrzezenia_knf',
            'opis': f'Reklama prowadzi do domeny {domena}, która jest na liście ostrzeżeń publicznych KNF. '
                    f'Wyświetlana w Polsce od {reklama["pierwsza"]:%d.%m.%Y} do {reklama["ostatnia"]:%d.%m.%Y}.',
            'podstawa': podstawa_knf(wpis),
        }],
    }


def rekord_drugiej_domeny(domena, wpis, druga, zebrano):
    return {
        'zrodlo': 'patrol_ostrzezen',
        'id_zrodla': druga['domena'],
        'platforma': 'www',
        'url': f'https://{druga["domena"]}/',
        'reklamodawca': None,
        'tekst': f'{druga["tytul"]} {druga["tekst"]}',
        'zebrano': zebrano,
        'opublikowano': None,
        'sygnaly': [{
            'modul': 'M3',
            'kod': 'druga_domena_ostrzezonej_strony',
            'opis': f'Ta sama strona co {domena} z listy ostrzeżeń publicznych KNF: '
                    f'zgodne {", ".join(druga["zgodne"])}. Tej domeny nie ma na liście.',
            'podstawa': podstawa_knf(wpis),
        }],
    }


def sygnal_cert(domena):
    if lista_cert.na_liscie(domena):
        kod, opis = 'na_liscie_cert', f'Domena {domena} jest na liście ostrzeżeń CERT Polska, więc operatorzy ją blokują.'
    else:
        kod, opis = 'brak_na_liscie_cert', f'Domeny {domena} nie ma na liście ostrzeżeń CERT Polska, więc operatorzy jej nie blokują.'
    return {'modul': 'M3', 'kod': kod, 'opis': opis, 'podstawa': 'Lista ostrzeżeń CERT Polska (hole.cert.pl)'}


def sprawdz(domena, wpis, przegladarka, ostrzezenia, z_cert):
    """Runs the checks for one domain; returns the ad counter text, the ads, the second domain and (record, picture) pairs."""
    zebrano = datetime.now(timezone.utc).isoformat(timespec='seconds')
    licznik, reklamy = reklamy_google.reklamy(przegladarka, domena)
    druga = druga_domena.znajdz(przegladarka, domena, ostrzezenia)
    rekordy = [(rekord_reklamy(domena, wpis, reklama, zebrano), reklama['obraz']) for reklama in reklamy]
    if druga:
        rekordy.append((rekord_drugiej_domeny(domena, wpis, druga, zebrano), druga['obraz']))
    if z_cert:
        for rekord, _ in rekordy:
            rekord['sygnaly'].append(sygnal_cert(rekord['url'].split('/')[2]))
    return licznik, reklamy, druga, rekordy


def obsluz(domena, ostrzezenia, przegladarka, z_cert):
    """Checks one domain and sends its records and pictures; returns added, skipped, errors (0 or 1) and the line to print."""
    dodane = obrazy = 0
    try:
        licznik, reklamy, druga, rekordy = sprawdz(domena, ostrzezenia[domena], przegladarka, ostrzezenia, z_cert)
        for rekord, obraz in rekordy:
            nowy, z_obrazem = wysylka.wyslij(rekord, obraz)
            dodane += nowy
            obrazy += z_obrazem
    except Exception as blad:
        return 0, 0, 1, f'{domena}: błąd: {type(blad).__name__} {" ".join(str(blad).split())[:200]}'
    pominiete = len(rekordy) - dodane
    linia = (f'{domena}: reklamy Google: {licznik}, otwarte {len(reklamy)}; '
             f'druga domena: {druga["domena"] if druga else "brak"}; dodane {dodane}, pominięte {pominiete}; obrazy {obrazy}')
    return dodane, pominiete, 0, linia


def wczytaj_cert():
    """True when the CERT Polska list loaded."""
    try:
        lista_cert.wczytaj()
        return True
    except Exception as blad:
        print(f'Nie udało się pobrać listy CERT Polska ({blad}), sprawdzam bez niej.')
        return False


def patroluj(domeny, ostrzezenia):
    from playwright.sync_api import sync_playwright

    z_cert = wczytaj_cert()
    dodane = pominiete = bledy = 0
    with sync_playwright() as playwright:
        przegladarka = playwright.chromium.launch(headless=True)
        for domena in domeny:
            nowe, juz_byly, blad, linia = obsluz(domena, ostrzezenia, przegladarka, z_cert)
            dodane += nowe
            pominiete += juz_byly
            bledy += blad
            print(linia)
        przegladarka.close()
    print(f'Podsumowanie: domen {len(domeny)}, dodane {dodane}, pominięte {pominiete}, błędy {bledy}')


if __name__ == '__main__':
    ostrzezenia = wczytaj_ostrzezenia()
    patroluj(sys.argv[1:] or list(ostrzezenia), ostrzezenia)
