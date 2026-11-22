# Sprawdzenie od końca do końca działającego stosu: docker compose up, potem pytest testy.
import uuid
from datetime import datetime

import httpx

API = 'http://localhost:8000'


def nowa_reklama(tekst='Zainwestuj 900 zł i zarabiaj 20 000 zł miesięcznie, zysk gwarantowany!'):
    return {
        'zrodlo': 'test',
        'id_zrodla': str(uuid.uuid4()),
        'platforma': 'facebook',
        'tekst': tekst,
        'zebrano': '2026-11-21T12:00:00Z',
    }


def test_reklama_przechodzi_cala_sciezke():
    reklama = nowa_reklama()

    dodana = httpx.post(f'{API}/reklamy', json=reklama, timeout=60)
    assert dodana.status_code == 201
    zapisana = dodana.json()
    assert zapisana['werdykt'] == 'oszustwo'
    assert zapisana['ryzyko'] > 0.5
    assert zapisana['status'] == 'nowa'
    assert isinstance(zapisana['powody'], list)
    assert 'rodzaj' in zapisana
    assert zapisana['werdykt_analityka'] is None

    powtorka = httpx.post(f'{API}/reklamy', json=reklama, timeout=60)
    assert powtorka.status_code == 409

    lista = httpx.get(f'{API}/reklamy', params={'werdykt': 'oszustwo', 'min_ryzyko': 0.5}).json()
    assert zapisana['id'] in [r['id'] for r in lista]
    assert lista == sorted(lista, key=lambda r: r['ryzyko'], reverse=True)

    zmieniona = httpx.patch(f'{API}/reklamy/{zapisana["id"]}', json={'status': 'w_toku'})
    assert zmieniona.json()['status'] == 'w_toku'

    oceniona = httpx.patch(f'{API}/reklamy/{zapisana["id"]}', json={'werdykt_analityka': 'oszustwo'}).json()
    assert oceniona['werdykt_analityka'] == 'oszustwo' and oceniona['status'] == 'w_toku'
    wyczyszczona = httpx.patch(f'{API}/reklamy/{zapisana["id"]}', json={'werdykt_analityka': None}).json()
    assert wyczyszczona['werdykt_analityka'] is None and wyczyszczona['status'] == 'w_toku'
    assert httpx.patch(f'{API}/reklamy/{zapisana["id"]}', json={}).status_code == 422


def test_platnik_spoza_rejestru_daje_sygnal():
    reklama = {**nowa_reklama(), 'reklamodawca': 'Tickmill Ltd'}
    zapisana = httpx.post(f'{API}/reklamy', json=reklama, timeout=180).json()
    assert zapisana['rejestr']['stan'] == 'spoza_rejestru'
    assert 'platnik_spoza_rejestru' in [s['kod'] for s in zapisana['sygnaly']]
    assert httpx.get(f'{API}/reklamy/{zapisana["id"]}').json()['rejestr'] == zapisana['rejestr']


def test_sygnal_zbieracza_zostaje_po_przeliczeniu():
    sygnal = {'modul': 'M3', 'kod': 'test_zbieracza', 'opis': 'Sygnał zbieracza', 'podstawa': ''}
    numer = httpx.post(f'{API}/reklamy', json={**nowa_reklama(), 'sygnaly': [sygnal]}, timeout=180).json()['id']
    zapisany = {**sygnal, 'firma': None}
    assert zapisany in httpx.get(f'{API}/reklamy/{numer}').json()['sygnaly']
    httpx.post(f'{API}/ucz', timeout=600).raise_for_status()
    assert zapisany in httpx.get(f'{API}/reklamy/{numer}').json()['sygnaly']


def test_data_publikacji_wraca_z_reklama():
    z_data = httpx.post(f'{API}/reklamy', json={**nowa_reklama(), 'opublikowano': '2026-11-20'}, timeout=180).json()
    assert z_data['opublikowano'] == '2026-11-20'
    bez_daty = httpx.post(f'{API}/reklamy', json=nowa_reklama(), timeout=180).json()
    assert bez_daty['opublikowano'] is None


def test_domena_wraca_z_reklama_i_zmienia_sie_przez_patch():
    z_domena = httpx.post(f'{API}/reklamy', json={**nowa_reklama(), 'domena': 'www.pekao.com.pl'}, timeout=180).json()
    assert z_domena['domena'] == 'www.pekao.com.pl'
    bez_domeny = httpx.post(f'{API}/reklamy', json=nowa_reklama(), timeout=180).json()
    assert bez_domeny['domena'] is None

    httpx.patch(f'{API}/reklamy/{bez_domeny["id"]}', json={'status': 'w_toku'}).raise_for_status()
    zmieniona = httpx.patch(f'{API}/reklamy/{bez_domeny["id"]}', json={'domena': 'zysk.example'}).json()
    assert zmieniona['domena'] == 'zysk.example' and zmieniona['status'] == 'w_toku'


def test_lista_od_daje_tylko_nowsze():
    pierwsza = httpx.post(f'{API}/reklamy', json=nowa_reklama(), timeout=180).json()
    druga = httpx.post(f'{API}/reklamy', json=nowa_reklama(), timeout=180).json()
    nowsze = httpx.get(f'{API}/reklamy', params={'od': pierwsza['dodano']}).json()
    od = datetime.fromisoformat(pierwsza['dodano'])
    assert all(datetime.fromisoformat(r['dodano']) > od for r in nowsze)
    assert druga['id'] in [r['id'] for r in nowsze]


def test_trzeci_niezwiazany_platnik_domeny_daje_sygnal_wszystkim_jej_reklamom():
    domena = uuid.uuid4().hex[:12] + '.example'

    def dodaj(platnik):
        reklama = {**nowa_reklama(), 'domena': domena, 'reklamodawca': platnik}
        return httpx.post(f'{API}/reklamy', json=reklama, timeout=180).json()['id']

    def z_sygnalem(numery):
        return [n for n in numery
                if 'wielu_platnikow_domeny' in [s['kod'] for s in httpx.get(f'{API}/reklamy/{n}').json()['sygnaly']]]

    numery = [dodaj('Jan Kowalczyk'), dodaj('Anna Wierzbicka')]
    assert z_sygnalem(numery) == []
    numery.append(dodaj('Piotr Zawadzki'))
    assert z_sygnalem(numery) == numery
    lista = httpx.get(f'{API}/reklamy').json()
    assert all('wielu_platnikow_domeny' in [s['kod'] for s in r['sygnaly']] for r in lista if r['id'] in numery)
    httpx.post(f'{API}/ucz', timeout=600).raise_for_status()
    assert z_sygnalem(numery) == numery


def test_nieznana_reklama_daje_404():
    assert httpx.get(f'{API}/reklamy/0').status_code == 404


def test_podobne_reklamy_znajduja_sie_nawzajem():
    # Kod unikalny dla tego przebiegu sprawia, że wiersze z wcześniejszych przebiegów są mniej podobne niż ta para.
    kod = uuid.uuid4().hex[:8]
    pierwsza = nowa_reklama(f'Kurs bitcoina rośnie, kod {kod}, zapisz się dziś i zarabiaj z nami codziennie.')
    druga = nowa_reklama(f'Kurs bitcoina rośnie, kod {kod}, zapisz się jutro i zarabiaj z nami codziennie.')
    pierwsza = httpx.post(f'{API}/reklamy', json=pierwsza, timeout=180).json()
    druga = httpx.post(f'{API}/reklamy', json=druga, timeout=180).json()

    podobne = httpx.get(f'{API}/reklamy/{pierwsza["id"]}/podobne').json()
    assert podobne[0]['id'] == druga['id']
    assert podobne[0]['podobienstwo'] >= 0.5
    assert pierwsza['id'] not in [r['id'] for r in podobne]


def test_model_zna_rodzaje_oszustw():
    assert len(httpx.get(f'{API}/rodzaje').json()) >= 4


def test_model_uczy_sie_od_analityka():
    numer = httpx.post(f'{API}/reklamy', json=nowa_reklama(), timeout=180).json()['id']
    try:
        httpx.patch(f'{API}/reklamy/{numer}', json={'werdykt_analityka': 'oszustwo'}).raise_for_status()
        nauka = httpx.post(f'{API}/ucz', timeout=600).json()
        assert nauka['przyklady'] >= 1 and nauka['przeliczono'] >= 1
    finally:
        # Zostawia model działającego stosu takim, jaki był przed testem.
        httpx.patch(f'{API}/reklamy/{numer}', json={'werdykt_analityka': None}).raise_for_status()
        httpx.post(f'{API}/ucz', timeout=600).raise_for_status()


def test_progi_maja_liczby_dla_suwaka():
    progi = httpx.get(f'{API}/progi').json()
    assert progi['oszustw'] > 0 and progi['uczciwych'] > 0
    assert {'prog', 'zlapane', 'falszywe_alarmy'} <= set(progi['progi'][0])
