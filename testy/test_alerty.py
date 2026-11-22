# Sprawdzenie kanału alertów na działającym stosie: docker compose up, potem pytest testy.
import base64
import json
import time

import httpx
import pytest

from test_nagranie import PROBKA_MOWY, dodaj_nagranie
from test_odczyt import PROBKA
from test_prog import zapisany_prog  # noqa: F401
from test_sciezka import API, nowa_reklama

pytest.importorskip('websockets')
from websockets.sync.client import connect  # noqa: E402

ALERTY = API.replace('http', 'ws') + '/alerty'
NIEWINNY_TEKST = 'Pizzeria Roma zaprasza na obiad. W każdy wtorek druga pizza za pół ceny, dowóz w Gdańsku.'


def alerty_przez(gniazdo, sekundy):
    """Każdy alert, który nadejdzie w podanym czasie; mogą trafić się też reklamy innych klientów stosu."""
    koniec = time.monotonic() + sekundy
    alerty = []
    while (zostalo := koniec - time.monotonic()) > 0:
        try:
            alerty.append(json.loads(gniazdo.recv(timeout=zostalo)))
        except TimeoutError:
            break
    return alerty


def test_domena_z_ostrzezenia_daje_alert():
    sygnal = {'modul': 'M3', 'kod': 'reklama_domeny_z_ostrzezenia_knf', 'opis': 'Domena z ostrzeżenia KNF',
              'podstawa': ''}
    with connect(ALERTY) as gniazdo:
        reklama = {**nowa_reklama(NIEWINNY_TEKST), 'sygnaly': [sygnal]}
        numer = httpx.post(f'{API}/reklamy', json=reklama, timeout=180).json()['id']
        alerty = [a for a in alerty_przez(gniazdo, 5) if a['id'] == numer]
    assert len(alerty) == 1
    assert set(alerty[0]) == {'id', 'reklamodawca', 'ryzyko', 'werdykt', 'zrodlo', 'dodano', 'ponad_progiem', 'poziom',
                              'powod'}
    assert alerty[0]['poziom'] == 'wysokie' and alerty[0]['powod'] == sygnal['opis']
    assert alerty[0]['ponad_progiem'] is False


def test_tekst_odczytany_z_obrazu_daje_alert():
    numer = httpx.post(f'{API}/reklamy', json=nowa_reklama(''), timeout=180).json()['id']
    obraz = base64.b64encode(PROBKA.read_bytes()).decode()
    with connect(ALERTY) as gniazdo:
        httpx.put(f'{API}/reklamy/{numer}/obraz', json={'obraz': obraz}, timeout=300).raise_for_status()
        alerty = [a for a in alerty_przez(gniazdo, 5) if a['id'] == numer]
    assert len(alerty) == 1
    assert alerty[0]['poziom'] == 'wysokie' and alerty[0]['ponad_progiem'] is True


def test_mowa_ponad_progiem_daje_alert(zapisany_prog):
    pierwsza = httpx.post(f'{API}/reklamy', json=nowa_reklama(''), timeout=180).json()['id']
    ryzyko = dodaj_nagranie(pierwsza, PROBKA_MOWY.read_bytes()).json()['ryzyko']
    # Angielskiej mowy model prawie nie zna, więc próg schodzi tuż pod jej ryzyko; ta sama mowa da je drugiej reklamie.
    httpx.put(f'{API}/prog', json={'prog': ryzyko - 0.001}).raise_for_status()
    numer = httpx.post(f'{API}/reklamy', json=nowa_reklama(''), timeout=180).json()['id']
    with connect(ALERTY) as gniazdo:
        dodaj_nagranie(numer, PROBKA_MOWY.read_bytes()).raise_for_status()
        alerty = [a for a in alerty_przez(gniazdo, 5) if a['id'] == numer]
    assert len(alerty) == 1
    assert alerty[0]['poziom'] == 'wysokie'


def test_zwykla_reklama_nie_daje_alertu():
    with connect(ALERTY) as gniazdo:
        zapisana = httpx.post(f'{API}/reklamy', json=nowa_reklama(NIEWINNY_TEKST), timeout=180).json()
        assert zapisana['werdykt'] == 'ok'
        assert zapisana['id'] not in [a['id'] for a in alerty_przez(gniazdo, 2)]
