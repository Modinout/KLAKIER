# Robotnik: bierze zadania z kolejki po kolei: linki wklejone w panelu oraz domeny, które sprawdza jak patrol.py.
# Użycie: python robotnik.py [linki]; z "linki" bierze tylko linki, więc link nigdy nie czeka na domenę.
import sys

from playwright.sync_api import sync_playwright

import kolejka
import patrol
import sprawdzenie_linku


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
            else:
                *_, linia = patrol.obsluz(zadanie, ostrzezenia, przegladarka, z_cert)
            print(linia, flush=True)


if __name__ == '__main__':
    pracuj(sys.argv[1:] == ['linki'])
