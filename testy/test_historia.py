# Check of the change history on a running stack: docker compose up, then pytest testy.
import sys
from datetime import datetime
from pathlib import Path

import httpx

from test_sciezka import API, nowa_reklama

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'api'))

from opis_zmian import zmiany_modelu  # noqa: E402

# How the panel sends a name with Polish letters: a header carries only Latin-1.
LUCJA = {'X-Analityk': '%C5%81ucja%20Wi%C5%9Bniewska'}


def zmien(numer, zmiana, naglowki=None):
    return httpx.patch(f'{API}/reklamy/{numer}', json=zmiana, headers=naglowki).raise_for_status().json()


def test_kazda_zmiana_analityka_trafia_do_historii():
    numer = httpx.post(f'{API}/reklamy', json=nowa_reklama(), timeout=180).json()['id']
    assert httpx.get(f'{API}/reklamy/{numer}/historia').json() == []

    zmieniona = zmien(numer, {'status': 'w_toku', 'notatka': 'Płatnik podaje cudzy NIP.'}, LUCJA)
    assert zmieniona['notatka'] == 'Płatnik podaje cudzy NIP.'
    assert httpx.get(f'{API}/reklamy/{numer}').json()['notatka'] == 'Płatnik podaje cudzy NIP.'
    zmien(numer, {'status': 'w_toku', 'werdykt_analityka': 'oszustwo'})
    zmien(numer, {'werdykt_analityka': None, 'domena': 'zysk.example', 'notatka': None}, LUCJA)

    historia = httpx.get(f'{API}/reklamy/{numer}/historia').json()
    assert [(wpis['kto'], wpis['co']) for wpis in historia] == [
        ('Łucja Wiśniewska', 'Notatka usunięta'),
        ('Łucja Wiśniewska', 'Domena: zysk.example'),
        ('Łucja Wiśniewska', 'Ocena analityka usunięta'),
        ('analityk', 'Ocena analityka: oszustwo'),
        ('Łucja Wiśniewska', 'Notatka zmieniona'),
        ('Łucja Wiśniewska', 'Status: nowa → w toku'),
    ]
    kiedy = [datetime.fromisoformat(wpis['kiedy']) for wpis in historia]
    assert kiedy == sorted(kiedy, reverse=True)


def test_notatka_wraca_na_liscie():
    numer = httpx.post(f'{API}/reklamy', json=nowa_reklama(), timeout=180).json()['id']
    zmien(numer, {'notatka': 'Sprawdzić stronę.'})
    assert [r['notatka'] for r in httpx.get(f'{API}/reklamy').json() if r['id'] == numer] == ['Sprawdzić stronę.']


def test_historia_nieznanej_reklamy_daje_404():
    odpowiedz = httpx.get(f'{API}/reklamy/0/historia')
    assert odpowiedz.status_code == 404
    assert odpowiedz.json()['detail'] == 'Nie ma takiej reklamy'


def test_przeliczenie_opisuje_tylko_reklamy_ze_zmiana():
    przed = {
        1: {'werdykt': 'ok', 'poziom': 'niskie'},
        2: {'werdykt': 'ok', 'poziom': 'niskie'},
        3: {'werdykt': 'do_sprawdzenia', 'poziom': 'niskie'},
        4: {'werdykt': 'ok', 'poziom': 'srednie'},
    }
    po = {
        1: {'werdykt': 'ok', 'poziom': 'niskie'},
        2: {'werdykt': 'oszustwo', 'poziom': 'wysokie'},
        3: {'werdykt': 'ok', 'poziom': 'niskie'},
        4: {'werdykt': 'ok', 'poziom': 'wysokie'},
        5: {'werdykt': 'oszustwo', 'poziom': 'wysokie'},
    }
    assert zmiany_modelu(przed, po) == [
        (2, 'Ocena modelu: ok → oszustwo, poziom ryzyka: niskie → wysokie'),
        (3, 'Ocena modelu: do sprawdzenia → ok'),
        (4, 'Poziom ryzyka: średnie → wysokie'),
    ]
