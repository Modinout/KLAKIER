# Worker: takes tasks from the queue one by one: links pasted in the panel, and domains it checks like patrol.py.
from playwright.sync_api import sync_playwright

import kolejka
import patrol
import sprawdzenie_linku


def pracuj():
    ostrzezenia = patrol.wczytaj_ostrzezenia()
    z_cert = patrol.wczytaj_cert()
    with sync_playwright() as playwright:
        przegladarka = playwright.chromium.launch(headless=True)
        print('Czekam na zadania.', flush=True)
        while True:
            lista, zadanie = kolejka.pobierz()
            if lista == kolejka.LINKI:
                linia = sprawdzenie_linku.obsluz(zadanie, ostrzezenia, przegladarka, z_cert)
            else:
                *_, linia = patrol.obsluz(zadanie, ostrzezenia, przegladarka, z_cert)
            print(linia, flush=True)


if __name__ == '__main__':
    pracuj()
