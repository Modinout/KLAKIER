# Zlecanie wyszukiwania frazy z panelu, na działającym stosie; samego wyszukiwania nie uruchamia.
import httpx

from test_sciezka import API


def test_pusta_i_za_dluga_fraza_daja_422():
    for fraza in ('', '   ', 'a' * 101):
        assert httpx.post(f'{API}/patrol', json={'fraza': fraza}).status_code == 422, fraza


def test_nieznane_wyszukiwanie_daje_404():
    assert httpx.get(f'{API}/patrol/0').status_code == 404


def test_ostatnie_wyszukiwanie_ma_stan_koncowy_albo_go_nie_ma():
    ostatnie = httpx.get(f'{API}/patrol')
    assert ostatnie.status_code == 200
    assert ostatnie.json() is None or ostatnie.json()['stan'] in ('gotowe', 'blad')
