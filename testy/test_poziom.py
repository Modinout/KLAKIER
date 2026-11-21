# Check of the risk level on a running stack: docker compose up, then pytest testy.
import httpx

from test_sciezka import API, nowa_reklama

NIEWINNY_TEKST = 'Pizzeria Roma zaprasza na obiad. W każdy wtorek druga pizza za pół ceny, dowóz w Gdańsku.'
OSZUSTWO = 'Zainwestuj 900 zł i zarabiaj 20 000 zł miesięcznie! Program dla każdego Polaka, zysk gwarantowany.'


def dodaj(reklama):
    return httpx.post(f'{API}/reklamy', json=reklama, timeout=180).json()


def test_domena_z_ostrzezenia_daje_poziom_wysoki():
    sygnal = {'modul': 'M3', 'kod': 'reklama_domeny_z_ostrzezenia_knf', 'opis': 'Domena z ostrzeżenia KNF',
              'podstawa': ''}
    zapisana = dodaj({**nowa_reklama(NIEWINNY_TEKST), 'sygnaly': [sygnal]})
    assert zapisana['poziom'] == 'wysokie'
    assert zapisana['powod'] == sygnal['opis']


def test_notatka_cert_nie_podnosi_poziomu():
    notatka = {'modul': 'M3', 'kod': 'brak_na_liscie_cert', 'opis': 'Domeny nie ma na liście CERT', 'podstawa': ''}
    zapisana = dodaj({**nowa_reklama(NIEWINNY_TEKST), 'sygnaly': [notatka]})
    assert zapisana['poziom'] == 'niskie'
    assert zapisana['powod'] is None


def test_tekst_oszustwa_daje_poziom_wysoki():
    zapisana = dodaj(nowa_reklama(OSZUSTWO))
    assert zapisana['poziom'] == 'wysokie'
    assert zapisana['powod'].startswith('Tekst reklamy wygląda na oszustwo')


def test_zwykla_reklama_ma_poziom_niski():
    zapisana = dodaj(nowa_reklama(NIEWINNY_TEKST))
    assert zapisana['poziom'] == 'niskie'
    assert httpx.get(f'{API}/reklamy/{zapisana["id"]}').json()['poziom'] == 'niskie'
