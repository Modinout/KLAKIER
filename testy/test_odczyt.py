# Odczyt obrazu reklamy przez działający stos: docker compose up, potem pytest testy.
import base64
import struct
import zlib
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


def png(szerokosc, wysokosc):
    def blok(rodzaj, dane):
        return struct.pack('>I', len(dane)) + rodzaj + dane + struct.pack('>I', zlib.crc32(rodzaj + dane))

    naglowek = struct.pack('>IIBBBBB', szerokosc, wysokosc, 8, 2, 0, 0, 0)
    return b'\x89PNG\r\n\x1a\n' + blok(b'IHDR', naglowek) + blok(b'IDAT', zlib.compress(bytes(30))) + blok(b'IEND', b'')


def test_obraz_za_duzy_do_odczytu_daje_422():
    obraz = base64.b64encode(png(65000, 65000)).decode()
    odpowiedz = httpx.post(f'{API}/odczytaj', json={'obraz': obraz}, timeout=120)
    assert odpowiedz.status_code == 422
