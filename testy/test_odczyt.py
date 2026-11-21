# Reading an ad image through a running stack: docker compose up, then pytest testy.
import base64
from pathlib import Path

import httpx

API = 'http://localhost:8000'
PROBKA = Path(__file__).resolve().parent.parent / 'odczyt' / 'probka.png'


def test_obraz_reklamy_daje_tekst():
    obraz = base64.b64encode(PROBKA.read_bytes()).decode()
    odpowiedz = httpx.post(f'{API}/odczytaj', json={'obraz': obraz}, timeout=120)
    assert odpowiedz.status_code == 200
    assert 'gwarantowany' in odpowiedz.json()['tekst'].lower()


def test_tekst_zamiast_obrazu_daje_422():
    obraz = base64.b64encode('to nie obraz'.encode()).decode()
    assert httpx.post(f'{API}/odczytaj', json={'obraz': obraz}, timeout=120).status_code == 422
