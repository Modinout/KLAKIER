# Check of the alert channel on a running stack: docker compose up, then pytest testy.
import json
import time

import httpx
import pytest

from test_sciezka import API, nowa_reklama

pytest.importorskip('websockets')
from websockets.sync.client import connect  # noqa: E402

ALERTY = API.replace('http', 'ws') + '/alerty'
NIEWINNY_TEKST = 'Pizzeria Roma zaprasza na obiad. W każdy wtorek druga pizza za pół ceny, dowóz w Gdańsku.'


def alerty_przez(gniazdo, sekundy):
    """Every alert that arrives within the given time; ads of other clients of the stack may show up too."""
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
    assert set(alerty[0]) == {'id', 'reklamodawca', 'ryzyko', 'werdykt', 'zrodlo', 'dodano', 'poziom', 'powod'}
    assert alerty[0]['poziom'] == 'wysokie' and alerty[0]['powod'] == sygnal['opis']


def test_zwykla_reklama_nie_daje_alertu():
    with connect(ALERTY) as gniazdo:
        zapisana = httpx.post(f'{API}/reklamy', json=nowa_reklama(NIEWINNY_TEKST), timeout=180).json()
        assert zapisana['werdykt'] == 'ok'
        assert zapisana['id'] not in [a['id'] for a in alerty_przez(gniazdo, 2)]
