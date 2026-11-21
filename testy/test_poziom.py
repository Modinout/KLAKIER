# Check of the risk level on a running stack: docker compose up, then pytest testy.
import httpx
import pytest

from test_sciezka import API, nowa_reklama

TWARDE_USTALENIA = ['reklama_domeny_z_ostrzezenia_knf', 'druga_domena_ostrzezonej_strony', 'wielu_platnikow_domeny',
                    'platnik_poza_listami', 'doradztwo_bez_zezwolenia']
MIEKKIE_USTALENIA = ['podatki_bez_zastrzezenia', 'platnik_spoza_rejestru']
NIEWINNY_TEKST = 'Pizzeria Roma zaprasza na obiad. W każdy wtorek druga pizza za pół ceny, dowóz w Gdańsku.'
OSZUSTWO = 'Zainwestuj 900 zł i zarabiaj 20 000 zł miesięcznie! Program dla każdego Polaka, zysk gwarantowany.'


def dodaj(reklama):
    return httpx.post(f'{API}/reklamy', json=reklama, timeout=180).json()


@pytest.mark.parametrize('kod', TWARDE_USTALENIA)
def test_twarde_ustalenie_daje_poziom_wysoki(kod):
    sygnal = {'modul': 'M1', 'kod': kod, 'opis': 'Opis ustalenia ' + kod, 'podstawa': ''}
    zapisana = dodaj({**nowa_reklama(NIEWINNY_TEKST), 'sygnaly': [sygnal]})
    assert zapisana['poziom'] == 'wysokie'
    assert zapisana['powod'] == sygnal['opis']


@pytest.mark.parametrize('kod', MIEKKIE_USTALENIA)
def test_inne_ustalenie_daje_poziom_sredni(kod):
    sygnal = {'modul': 'M1', 'kod': kod, 'opis': 'Opis ustalenia ' + kod, 'podstawa': ''}
    zapisana = dodaj({**nowa_reklama(NIEWINNY_TEKST), 'sygnaly': [sygnal]})
    assert zapisana['poziom'] == 'srednie'
    assert zapisana['powod'] == sygnal['opis']


def test_notatka_cert_nie_podnosi_poziomu():
    notatka = {'modul': 'M3', 'kod': 'brak_na_liscie_cert', 'opis': 'Domeny nie ma na liście CERT', 'podstawa': ''}
    zapisana = dodaj({**nowa_reklama(NIEWINNY_TEKST), 'sygnaly': [notatka]})
    assert zapisana['poziom'] == 'niskie'
    assert zapisana['powod'] is None


def test_tekst_oszustwa_daje_poziom_wysoki():
    zapisana = dodaj(nowa_reklama(OSZUSTWO))
    assert zapisana['poziom'] == 'wysokie'
    assert zapisana['powod'].startswith('Treść typowa dla fałszywych inwestycji')


def test_zwykla_reklama_ma_poziom_niski():
    zapisana = dodaj(nowa_reklama(NIEWINNY_TEKST))
    assert zapisana['poziom'] == 'niskie'
    assert httpx.get(f'{API}/reklamy/{zapisana["id"]}').json()['poziom'] == 'niskie'
