from datetime import datetime

import httpx
import pytest

import meta_api
import wysylka

NASTEPNA = 'https://graph.facebook.com/v27.0/ads_archive?after=QVFI&search_terms=inwestowanie'
REKLAMA_A = {
    'id': '111', 'page_name': 'Strona A', 'publisher_platforms': ['INSTAGRAM', 'FACEBOOK'],
    'ad_delivery_start_time': '2026-11-20T10:00:00+0000', 'ad_creative_bodies': ['  Inwestuj z nami\n'],
    'ad_creative_link_titles': ['Tytuł'], 'ad_creative_link_captions': ['Przyklad.PL'],
}
SZABLON = {
    'id': '222', 'page_name': 'Strona B', 'ad_creative_bodies': ['{{product.brand}}'],
    'ad_creative_link_titles': ['Zyski bez ryzyka'], 'ad_creative_link_captions': ['facebook.com'],
}
DRUGA_STRONA = {'id': '333', 'page_name': 'Strona C', 'publisher_platforms': ['MESSENGER'],
                'ad_creative_bodies': ['Trading dla każdego']}
ODPOWIEDZI = {
    'inwestowanie': {'data': [REKLAMA_A, SZABLON], 'paging': {'cursors': {'after': 'QVFI'}, 'next': NASTEPNA}},
    NASTEPNA: {'data': [DRUGA_STRONA], 'paging': {'cursors': {'after': 'QVFJ'}}},
    'forex': {'data': [REKLAMA_A]},
}


class Zegar(datetime):
    @classmethod
    def now(cls, tz=None):
        return datetime(2026, 11, 22, 12, 0, tzinfo=tz)


class Zapytania(list):
    wyslane = None


@pytest.fixture
def zapytania(monkeypatch):
    """Records every request and every record sent; the library answers from ODPOWIEDZI, a phrase it does not know has no ads."""
    zapytania, wyslane = Zapytania(), []

    def pobierz(adres, params=None, **_):
        zapytania.append((adres, params))
        klucz = params['search_terms'] if params else adres
        return httpx.Response(200, json=ODPOWIEDZI.get(klucz, {'data': []}))

    monkeypatch.setattr(meta_api.httpx, 'get', pobierz)
    monkeypatch.setattr(wysylka, 'dodaj', lambda rekord: (wyslane.append(rekord) or True, rekord))
    monkeypatch.setattr(meta_api, 'datetime', Zegar)
    monkeypatch.setenv('META_TOKEN', 'tajny')
    zapytania.wyslane = wyslane
    return zapytania


def test_zapytanie_o_kazda_fraze_z_polska_i_oknem_dat(zapytania):
    assert meta_api.przeszukaj() == 0
    pierwsze = [params for adres, params in zapytania if params]
    assert [params['search_terms'] for params in pierwsze] == meta_api.FRAZY
    assert pierwsze[0] == {
        'access_token': 'tajny', 'ad_reached_countries': "['PL']", 'ad_type': 'ALL', 'ad_active_status': 'ALL',
        'ad_delivery_date_min': '2026-11-20', 'search_terms': 'inwestowanie', 'fields': meta_api.POLA,
    }


def test_nastepna_strona_z_linku_bez_zmian(zapytania):
    meta_api.przeszukaj()
    assert (NASTEPNA, None) in zapytania
    assert [reklama['id_zrodla'] for reklama in zapytania.wyslane] == ['111', '222', '333']


def test_ta_sama_reklama_z_dwoch_fraz_idzie_raz(zapytania, capsys):
    meta_api.przeszukaj()
    assert [reklama['id_zrodla'] for reklama in zapytania.wyslane].count('111') == 1
    assert 'forex: reklamy Mety 1, dodane 0' in capsys.readouterr().out


def test_rekord_pole_po_polu(zapytania):
    meta_api.przeszukaj()
    assert zapytania.wyslane[0] == {
        'zrodlo': 'meta_ads',
        'id_zrodla': '111',
        'platforma': 'instagram',
        'url': 'https://www.facebook.com/ads/library/?id=111',
        'domena': 'przyklad.pl',
        'reklamodawca': 'Strona A',
        'tekst': 'Inwestuj z nami',
        'zebrano': '2026-11-22T12:00:00+00:00',
        'opublikowano': '2026-11-20',
    }


def test_szablon_bierze_tytul_a_adres_mety_nie_daje_domeny(zapytania):
    meta_api.przeszukaj()
    szablon = zapytania.wyslane[1]
    assert szablon['tekst'] == 'Zyski bez ryzyka'
    assert szablon['domena'] is None


def test_reklama_bez_daty_i_platformy(zapytania):
    meta_api.przeszukaj()
    assert zapytania.wyslane[1]['reklamodawca'] == 'Strona B'
    assert zapytania.wyslane[1]['opublikowano'] is None
    assert zapytania.wyslane[1]['platforma'] == 'facebook'
    assert zapytania.wyslane[2]['platforma'] == 'messenger'


@pytest.mark.parametrize('podpis, oczekiwana', [
    ('XTB.COM/pl', 'xtb.com'),
    (' Przyklad.pl ', 'przyklad.pl'),
    ('Wypełnij formularz', None),
    ('Dowiedz się więcej', None),
    ('formularz', None),
    ('facebook.com', None),
    ('www.instagram.com/oferta', None),
    ('', None),
])
def test_domena_z_podpisu_tylko_gdy_to_host_poza_meta(podpis, oczekiwana):
    assert meta_api.domena({'ad_creative_link_captions': [podpis]}) == oczekiwana


def test_domena_bez_podpisu():
    assert meta_api.domena({}) is None


def test_bez_tokenu_nic_nie_pyta(zapytania, monkeypatch, capsys):
    monkeypatch.delenv('META_TOKEN')
    assert meta_api.przeszukaj() == 0
    assert zapytania == []
    assert 'Brak META_TOKEN' in capsys.readouterr().out


def test_pusty_token_nic_nie_pyta(zapytania, monkeypatch):
    monkeypatch.setenv('META_TOKEN', '')
    assert meta_api.przeszukaj() == 0
    assert zapytania == []


def test_blad_tokenu_konczy_z_kodem_i_logiem(monkeypatch, capsys):
    blad = {'error': {'code': 190, 'message': 'Invalid OAuth access token.'}}
    monkeypatch.setattr(meta_api.httpx, 'get', lambda adres, params=None, **_: httpx.Response(400, json=blad))
    monkeypatch.setenv('META_TOKEN', 'zly')
    assert meta_api.przeszukaj() == 1
    assert '190 Invalid OAuth access token.' in capsys.readouterr().out
