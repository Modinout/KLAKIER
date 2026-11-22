import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'api'))

from ostrzezenie_strony import sygnaly  # noqa: E402

API = 'http://localhost:8000'
DOMENA = 'broker.example'


def widok(px=16, przewazajacy=16, kontrast=21, pogrubienie=400, widoczne=True, ostrzezenie=True, cfd=True):
    return {
        'adres': f'https://{DOMENA}/',
        'przewazajacy_px': przewazajacy,
        'cfd': cfd,
        'ostrzezenie': {
            'tekst': '76% rachunków inwestorów detalicznych odnotowuje straty.',
            'px': px,
            'pogrubienie': pogrubienie,
            'kontrast': kontrast,
            'widoczne': widoczne,
            'bez_przewijania': widoczne,
        } if ostrzezenie else None,
    }


def strona(komputer, telefon=None, tablet=None):
    return {'domena': DOMENA, 'zmierzono': datetime(2026, 11, 22, 3, tzinfo=timezone.utc),
            'komputer': komputer, 'tablet': tablet, 'telefon': telefon}


def opis(komputer, telefon=None):
    sygnal, = sygnaly(DOMENA, strona(komputer, telefon))
    assert sygnal['modul'] == 'M2' and sygnal['kod'] == 'ostrzezenie_nieczytelne'
    return sygnal['opis']


def test_czytelne_ostrzezenie_nie_daje_sygnalu():
    assert sygnaly(DOMENA, strona(widok(), widok())) == []


def test_mniejsza_czcionka_niz_reszta_tekstu():
    assert opis(widok(px=12), widok()) == (
        'Ostrzeżenie o ryzyku na stronie broker.example: na komputerze mniejsze niż reszta tekstu (12 px przy 16 px).')


def test_slaby_kontrast_i_brak_na_telefonie():
    assert opis(widok(kontrast=2.32), widok(widoczne=False)) == (
        'Ostrzeżenie o ryzyku na stronie broker.example: na komputerze słabo odcina się od tła (kontrast 2,32:1); '
        'na telefonie niewidoczne.')


def test_na_telefonie_bez_ostrzezenia_w_ogole():
    assert opis(widok(), widok(ostrzezenie=False)).endswith(': na telefonie niewidoczne.')


def test_na_tablecie_niewidoczne():
    sygnal, = sygnaly(DOMENA, strona(widok(), widok(), tablet=widok(widoczne=False)))
    assert sygnal['opis'] == 'Ostrzeżenie o ryzyku na stronie broker.example: na tablecie niewidoczne.'
    assert '(komputer 1366 px, tablet 768 px, telefon 390 px)' in sygnal['podstawa']


def test_duzy_pogrubiony_tekst_potrzebuje_mniejszego_kontrastu():
    assert sygnaly(DOMENA, strona(widok(px=19, kontrast=3.5, pogrubienie=700))) == []
    assert 'kontrast 3,5:1' in opis(widok(px=19, kontrast=3.5))


def test_nieznany_kontrast_nie_daje_sygnalu():
    assert sygnaly(DOMENA, strona(widok(kontrast=None))) == []


def test_brak_ostrzezenia_na_stronie_o_cfd():
    sygnal, = sygnaly(DOMENA, strona(widok(ostrzezenie=False), widok(widoczne=False)))
    assert sygnal['kod'] == 'brak_ostrzezenia_strony'
    assert '22.11.2026' in sygnal['podstawa']


def test_brak_ostrzezenia_bez_cfd_nie_daje_sygnalu():
    assert sygnaly(DOMENA, strona(widok(ostrzezenie=False, cfd=False))) == []


def test_bez_pomiaru_nie_ma_sygnalu():
    assert sygnaly(DOMENA, None) == []


def test_reklama_dostaje_ustalenie_ze_strony_swojej_domeny():
    domena = uuid.uuid4().hex[:12] + '.example'

    def kody(numer):
        return [s['kod'] for s in httpx.get(f'{API}/reklamy/{numer}').json()['sygnaly']]

    zapisana = httpx.put(f'{API}/strony/{domena}', json={'komputer': widok(px=11), 'telefon': None})
    assert zapisana.status_code == 200 and zapisana.json()['domena'] == domena
    reklama = {'zrodlo': 'test', 'id_zrodla': str(uuid.uuid4()), 'platforma': 'google', 'domena': domena,
               'tekst': 'Otwórz rachunek maklerski.', 'zebrano': '2026-11-22T03:00:00Z'}
    numer = httpx.post(f'{API}/reklamy', json=reklama, timeout=180).json()['id']
    assert 'ostrzezenie_nieczytelne' in kody(numer)

    httpx.put(f'{API}/strony/{domena}', json={'komputer': widok(), 'telefon': widok()}).raise_for_status()
    assert 'ostrzezenie_nieczytelne' not in kody(numer)
