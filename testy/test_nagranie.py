# Nagranie reklamy wideo na działającym stosie: docker compose up, potem pytest testy.
import base64
import io
import wave
from pathlib import Path

import httpx

from test_sciezka import API, nowa_reklama

NAJWIEKSZE_NAGRANIE = 50 * 1024 * 1024 * 4 // 3 + 4
PROBKA_MOWY = Path(__file__).resolve().parent.parent / 'odczyt' / 'probka_mowa.mp3'


def cisza():
    bufor = io.BytesIO()
    with wave.open(bufor, 'wb') as plik:
        plik.setnchannels(1)
        plik.setsampwidth(2)
        plik.setframerate(16000)
        plik.writeframes(bytes(2 * 16000))
    return bufor.getvalue()


def dodaj_nagranie(numer, bajty):
    nagranie = base64.b64encode(bajty).decode()
    return httpx.put(f'{API}/reklamy/{numer}/nagranie', json={'nagranie': nagranie}, timeout=360)


def test_nagranie_nieznanej_reklamy_daje_404():
    assert dodaj_nagranie(0, cisza()).status_code == 404


def test_za_duze_nagranie_daje_422():
    numer = httpx.post(f'{API}/reklamy', json=nowa_reklama(), timeout=180).json()['id']
    nagranie = 'A' * (NAJWIEKSZE_NAGRANIE + 4)
    odpowiedz = httpx.put(f'{API}/reklamy/{numer}/nagranie', json={'nagranie': nagranie}, timeout=120)
    assert odpowiedz.status_code == 422
    assert odpowiedz.json()['detail'] == 'Nagranie jest większe niż 50 MB.'


def test_nagranie_daje_mowe_i_wpis_w_historii():
    numer = httpx.post(f'{API}/reklamy', json=nowa_reklama(), timeout=180).json()['id']
    odpowiedz = dodaj_nagranie(numer, cisza())
    assert odpowiedz.status_code == 200
    assert isinstance(odpowiedz.json()['mowa'], str)
    assert isinstance(odpowiedz.json()['ponad_progiem'], bool)
    historia = httpx.get(f'{API}/reklamy/{numer}/historia').json()
    assert [wpis['co'] for wpis in historia if wpis['co'].startswith('Dodano nagranie')]


def test_ocena_zmieniona_przez_mowe_trafia_do_historii():
    numer = httpx.post(f'{API}/reklamy', json=nowa_reklama(''), timeout=180).json()['id']
    assert dodaj_nagranie(numer, PROBKA_MOWY.read_bytes()).json()['werdykt'] == 'ok'
    historia = httpx.get(f'{API}/reklamy/{numer}/historia').json()
    assert [(wpis['kto'], wpis['co']) for wpis in historia[:1]] == [('analityk', 'Ocena modelu: do sprawdzenia → ok')]
    assert historia[1]['co'].startswith('Dodano nagranie')


def test_tekst_zamiast_dzwieku_daje_422():
    numer = httpx.post(f'{API}/reklamy', json=nowa_reklama(), timeout=180).json()['id']
    assert dodaj_nagranie(numer, 'to nie jest dźwięk'.encode()).status_code == 422
