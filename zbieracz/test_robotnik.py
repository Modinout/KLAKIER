import json

import pytest

import kolejka
import tiktok

pytest.importorskip('playwright.sync_api')
import robotnik


def stany_po(monkeypatch, fraza, wyniki):
    zapisane = []
    monkeypatch.setattr(kolejka, 'zapisz_wyszukiwanie', lambda id, stan: zapisane.append((id, dict(stan))))
    monkeypatch.setattr(tiktok, 'obsluz', lambda fraza, przegladarka: wyniki[fraza])
    linie = robotnik.szukaj_frazy(json.dumps({'id': 7, 'fraza': fraza}), None)
    return linie, zapisane


def test_udane_wyszukiwanie_zapisuje_liczby(monkeypatch):
    linie, zapisane = stany_po(monkeypatch, 'forex', {'forex': (3, 5, 0, 'forex: dodane 3')})
    assert linie == 'forex: dodane 3'
    assert zapisane[0] == (7, {'fraza': 'forex', 'stan': 'w_toku'})
    id, koniec = zapisane[1]
    assert (id, koniec['stan'], koniec['dodane'], koniec['pominiete']) == (7, 'gotowe', 3, 5)
    assert koniec['kiedy']


def test_bez_frazy_szuka_fraz_inwestycyjnych_i_sumuje(monkeypatch):
    wyniki = {fraza: (1, 2, 0, fraza) for fraza in tiktok.FRAZY}
    wyniki[tiktok.FRAZY[0]] = (0, 0, 1, 'błąd')
    linie, zapisane = stany_po(monkeypatch, None, wyniki)
    koniec = zapisane[1][1]
    reszta = len(tiktok.FRAZY) - 1
    assert (koniec['stan'], koniec['dodane'], koniec['pominiete']) == ('gotowe', reszta, 2 * reszta)
    assert linie.count('\n') == reszta


def test_nieudane_wyszukiwanie_zapisuje_powod(monkeypatch):
    _, zapisane = stany_po(monkeypatch, 'forex', {'forex': (0, 0, 1, 'forex: błąd')})
    koniec = zapisane[1][1]
    assert koniec['stan'] == 'blad' and koniec['blad'] and 'dodane' not in koniec
