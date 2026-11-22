# Robotnik: bierze zadania z kolejki po kolei: linki wklejone w panelu, frazy do wyszukania w bibliotece reklam TikToka
# oraz domeny, które sprawdza jak patrol.py.
# Użycie: python robotnik.py [linki]; z "linki" nie bierze domen, więc link i fraza nigdy nie czekają na domenę.
import json
import sys
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

import kolejka
import patrol
import sprawdzenie_linku
import tiktok


def szukaj_frazy(zadanie, przegladarka):
    """Szuka frazy zleconej w panelu, a bez frazy fraz inwestycyjnych, i zapisuje w kolejce, jak poszło; zwraca linie do wydruku."""
    zlecenie = json.loads(zadanie)
    stan = {'fraza': zlecenie['fraza'], 'stan': 'w_toku'}
    kolejka.zapisz_wyszukiwanie(zlecenie['id'], stan)
    frazy = [zlecenie['fraza']] if zlecenie['fraza'] else tiktok.FRAZY
    wyniki = [tiktok.obsluz(fraza, przegladarka) for fraza in frazy]
    if all(blad for _, _, blad, _ in wyniki):
        stan |= {'stan': 'blad', 'blad': 'Biblioteka reklam TikToka nie odpowiedziała. Spróbuj ponownie.'}
    else:
        stan |= {'stan': 'gotowe', 'dodane': sum(w[0] for w in wyniki), 'pominiete': sum(w[1] for w in wyniki)}
    stan['kiedy'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    kolejka.zapisz_wyszukiwanie(zlecenie['id'], stan)
    return '\n'.join(linia for *_, linia in wyniki)


def pracuj(tylko_linki):
    ostrzezenia = patrol.wczytaj_ostrzezenia()
    z_cert = patrol.wczytaj_cert()
    with sync_playwright() as playwright:
        przegladarka = playwright.chromium.launch(headless=True)
        print('Czekam na zadania.', flush=True)
        while True:
            lista, zadanie = kolejka.pobierz(tylko_linki)
            if not przegladarka.is_connected():
                przegladarka = playwright.chromium.launch(headless=True)
            if lista == kolejka.LINKI:
                linia = sprawdzenie_linku.obsluz(zadanie, ostrzezenia, przegladarka, z_cert)
            elif lista == kolejka.FRAZY:
                linia = szukaj_frazy(zadanie, przegladarka)
            else:
                *_, linia = patrol.obsluz(zadanie, ostrzezenia, przegladarka, z_cert)
            print(linia, flush=True)


if __name__ == '__main__':
    pracuj(sys.argv[1:] == ['linki'])
