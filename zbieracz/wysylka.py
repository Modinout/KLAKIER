# Wysyła rekordy i ich obrazy do api.
import base64
import os

import httpx

# Rekordy już w api, według (zrodlo, id_zrodla); pełna lista jest pobierana tylko wtedy, gdy duplikatu tu nie ma.
zapisane = {}


def dodaj(rekord):
    """Zwraca, czy rekord jest nowy, i rekord w postaci zapisanej w api."""
    odpowiedz = httpx.post(f"{os.environ['API_URL']}/reklamy", json=rekord, timeout=120)
    if odpowiedz.status_code == 409:
        klucz = (rekord['zrodlo'], rekord['id_zrodla'])
        if klucz not in zapisane:
            wczytaj_zapisane()
        return False, zapisane[klucz]
    odpowiedz.raise_for_status()
    return True, zapamietaj(odpowiedz.json())


def wyslij(rekord, obraz):
    """Wysyła rekord, potem jego obraz; zwraca, czy rekord jest nowy i czy obraz poszedł.

    Obraz idzie także do rekordu, który api już ma bez obrazu lub bez tekstu,
    więc drugi przebieg naprawia starsze rekordy: api czyta tekst tylko dla rekordu z pustym tekstem.
    """
    nowy, zapisany = dodaj(rekord)
    if obraz and not (zapisany['ma_obraz'] and zapisany['tekst']):
        wyslij_obraz(zapisany['id'], obraz)
        return nowy, True
    return nowy, False


def wyslij_obraz(id, obraz):
    # Api czyta tekst z obrazu, co trwa sekundy na obraz.
    odpowiedz = httpx.put(f"{os.environ['API_URL']}/reklamy/{id}/obraz",
                          json={'obraz': base64.b64encode(obraz).decode()}, timeout=300)
    odpowiedz.raise_for_status()
    zapamietaj(odpowiedz.json())


def wczytaj_zapisane():
    odpowiedz = httpx.get(f"{os.environ['API_URL']}/reklamy", timeout=120)
    odpowiedz.raise_for_status()
    for reklama in odpowiedz.json():
        zapamietaj(reklama)


def zapamietaj(reklama):
    zapisane[(reklama['zrodlo'], reklama['id_zrodla'])] = reklama
    return reklama
