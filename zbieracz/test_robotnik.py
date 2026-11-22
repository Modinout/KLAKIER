import json

import kolejka
import robotnik
import tiktok


def stany_po(monkeypatch, wynik):
    zapisane = []
    monkeypatch.setattr(kolejka, 'zapisz_wyszukiwanie', lambda id, stan: zapisane.append((id, dict(stan))))
    monkeypatch.setattr(tiktok, 'obsluz', lambda fraza, przegladarka: wynik)
    linia = robotnik.szukaj_frazy(json.dumps({'id': 7, 'fraza': 'forex'}), None)
    return linia, zapisane


def test_udane_wyszukiwanie_zapisuje_liczby(monkeypatch):
    linia, zapisane = stany_po(monkeypatch, (3, 5, 0, 'forex: dodane 3'))
    assert linia == 'forex: dodane 3'
    assert zapisane[0] == (7, {'fraza': 'forex', 'stan': 'w_toku'})
    id, koniec = zapisane[1]
    assert (id, koniec['stan'], koniec['dodane'], koniec['pominiete']) == (7, 'gotowe', 3, 5)
    assert koniec['kiedy']


def test_nieudane_wyszukiwanie_zapisuje_powod(monkeypatch):
    _, zapisane = stany_po(monkeypatch, (0, 0, 1, 'forex: błąd'))
    koniec = zapisane[1][1]
    assert koniec['stan'] == 'blad' and koniec['blad'] and 'dodane' not in koniec
