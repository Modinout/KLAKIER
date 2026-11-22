# Check of the young landing domain finding on a running stack: docker compose up, then pytest testy.
import sys
import uuid
from datetime import date, timedelta
from pathlib import Path

import httpx

from test_sciezka import API, nowa_reklama

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'api'))

from wiek_domeny import sygnaly  # noqa: E402

INWESTYCJA = 'Otwórz konto maklerskie i inwestuj w akcje oraz ETF z prowizją 0 zł.'
PIZZERIA = 'Pizzeria Roma zaprasza na obiad. W każdy wtorek druga pizza za pół ceny, dowóz w Gdańsku.'


def reklama(tekst=INWESTYCJA, opublikowano=date(2026, 11, 20)):
    return {'tekst': tekst, 'reklamodawca': None, 'domena': 'zysk.example', 'opublikowano': opublikowano}


def kody(lista):
    return [sygnal['kod'] for sygnal in lista]


def test_domena_zarejestrowana_mniej_niz_30_dni_przed_publikacja_daje_sygnal():
    assert kody(sygnaly(reklama(), date(2026, 10, 22))) == ['mloda_domena']
    assert kody(sygnaly(reklama(), date(2026, 11, 20))) == ['mloda_domena']
    assert sygnaly(reklama(), date(2026, 10, 21)) == []
    assert sygnaly(reklama(), date(2026, 11, 21)) == []
    assert sygnaly(reklama(), None) == []


def test_bez_daty_publikacji_liczy_sie_dzisiaj():
    assert kody(sygnaly(reklama(opublikowano=None), date.today() - timedelta(days=3))) == ['mloda_domena']
    assert sygnaly(reklama(opublikowano=None), date.today() - timedelta(days=40)) == []


def test_reklama_spoza_inwestycji_nie_daje_sygnalu():
    assert sygnaly(reklama(PIZZERIA), date(2026, 11, 10)) == []


def test_mloda_domena_reklamy_inwestycyjnej_daje_poziom_sredni():
    mloda, stara = uuid.uuid4().hex[:12] + '.example', uuid.uuid4().hex[:12] + '.example'
    piec_dni_temu = (date.today() - timedelta(days=5)).isoformat()
    zapisana = httpx.put(f'{API}/domeny/{mloda}', json={'zarejestrowano': piec_dni_temu}).json()
    assert zapisana['domena'] == mloda and zapisana['zarejestrowano'] == piec_dni_temu
    httpx.put(f'{API}/domeny/{stara}', json={'zarejestrowano': '2001-05-01'}).raise_for_status()

    def dodaj(tekst, domena):
        return httpx.post(f'{API}/reklamy', json={**nowa_reklama(tekst), 'domena': domena}, timeout=180).json()

    inwestycyjna = dodaj(INWESTYCJA, mloda)
    assert kody(inwestycyjna['sygnaly']) == ['mloda_domena']
    assert inwestycyjna['sygnaly'][0]['modul'] == 'M1'
    assert inwestycyjna['poziom'] == 'srednie'
    assert kody(httpx.get(f'{API}/reklamy/{inwestycyjna["id"]}').json()['sygnaly']) == ['mloda_domena']
    assert kody(dodaj(PIZZERIA, mloda)['sygnaly']) == []
    assert kody(dodaj(INWESTYCJA, stara)['sygnaly']) == []
