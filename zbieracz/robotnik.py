# Worker: takes domains from the patrol queue one by one and checks them like patrol.py.
from playwright.sync_api import sync_playwright

import kolejka
import patrol


def pracuj():
    ostrzezenia = patrol.wczytaj_ostrzezenia()
    z_cert = patrol.wczytaj_cert()
    with sync_playwright() as playwright:
        przegladarka = playwright.chromium.launch(headless=True)
        print('Czekam na zadania.', flush=True)
        while True:
            domena = kolejka.pobierz()
            *_, linia = patrol.obsluz(domena, ostrzezenia, przegladarka, z_cert)
            print(linia, flush=True)


if __name__ == '__main__':
    pracuj()
