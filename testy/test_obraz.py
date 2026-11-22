# Obraz reklamy na działającym stosie: docker compose up, potem pytest testy.
import base64

import httpx

from test_odczyt import PROBKA
from test_sciezka import API, nowa_reklama

# PNG 1x1.
MALY_PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
)


def dodana_reklama(tekst):
    return httpx.post(f'{API}/reklamy', json=nowa_reklama(tekst), timeout=180).json()


def test_obraz_reklamy_z_tekstem_zostaje_zapisany():
    reklama = dodana_reklama('Pizzeria Roma zaprasza na obiad w każdy wtorek.')
    assert reklama['ma_obraz'] is False
    obraz = base64.b64encode(MALY_PNG).decode()
    zapisana = httpx.put(f'{API}/reklamy/{reklama["id"]}/obraz', json={'obraz': obraz}, timeout=60)
    assert zapisana.status_code == 200
    assert zapisana.json()['tekst'] == reklama['tekst']
    assert zapisana.json()['ma_obraz'] is True
    assert zapisana.json()['ponad_progiem'] is False

    pobrany = httpx.get(f'{API}/reklamy/{reklama["id"]}/obraz')
    assert pobrany.content == MALY_PNG
    assert pobrany.headers['content-type'] == 'image/png'


def test_tekst_zamiast_obrazu_daje_422():
    numer = dodana_reklama('Pizzeria Roma zaprasza na obiad w każdy wtorek.')['id']
    obraz = base64.b64encode('to nie obraz'.encode()).decode()
    assert httpx.put(f'{API}/reklamy/{numer}/obraz', json={'obraz': obraz}).status_code == 422


def test_obraz_nieznanej_reklamy_daje_404():
    obraz = base64.b64encode(MALY_PNG).decode()
    odpowiedz = httpx.put(f'{API}/reklamy/0/obraz', json={'obraz': obraz})
    assert odpowiedz.status_code == 404
    assert odpowiedz.json()['detail'] == 'Nie ma takiej reklamy'


def test_reklama_bez_obrazu_daje_404():
    numer = dodana_reklama('Pizzeria Roma zaprasza na obiad w każdy wtorek.')['id']
    odpowiedz = httpx.get(f'{API}/reklamy/{numer}/obraz')
    assert odpowiedz.status_code == 404
    assert odpowiedz.json()['detail'] == 'Ta reklama nie ma obrazu'


def test_obraz_reklamy_bez_tekstu_daje_tekst():
    numer = dodana_reklama('')['id']
    obraz = base64.b64encode(PROBKA.read_bytes()).decode()
    zapisana = httpx.put(f'{API}/reklamy/{numer}/obraz', json={'obraz': obraz}, timeout=300).json()
    assert 'gwarantowany' in zapisana['tekst'].lower()
    assert zapisana['ponad_progiem'] is True
    historia = httpx.get(f'{API}/reklamy/{numer}/historia').json()
    assert [(wpis['kto'], wpis['co']) for wpis in historia] == [
        ('model', 'Ocena modelu: do sprawdzenia → oszustwo, poziom ryzyka: niskie → wysokie')]
