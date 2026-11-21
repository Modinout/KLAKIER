# Sends records and their pictures to the api.
import base64
import os

import httpx

# Records already in the api, by (zrodlo, id_zrodla); the full list is fetched only when a duplicate is not here.
zapisane = {}


def dodaj(rekord):
    """Returns whether the record is new and the record as stored in the api."""
    odpowiedz = httpx.post(f"{os.environ['API_URL']}/reklamy", json=rekord, timeout=120)
    if odpowiedz.status_code == 409:
        klucz = (rekord['zrodlo'], rekord['id_zrodla'])
        if klucz not in zapisane:
            wczytaj_zapisane()
        return False, zapisane[klucz]
    odpowiedz.raise_for_status()
    return True, zapamietaj(odpowiedz.json())


def wyslij(rekord, obraz):
    """Sends the record, then its picture; returns whether the record is new and whether the picture went.

    A picture goes also to a record the api already has without a picture or without text,
    so a second run repairs older records: the api reads the text only for a record whose text is empty.
    """
    nowy, zapisany = dodaj(rekord)
    if obraz and not (zapisany['ma_obraz'] and zapisany['tekst']):
        wyslij_obraz(zapisany['id'], obraz)
        return nowy, True
    return nowy, False


def wyslij_obraz(id, obraz):
    # The api reads the text from the picture, which takes seconds per picture.
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
