# End-to-end check of a running stack: docker compose up, then pytest testy.
import uuid

import httpx

API = 'http://localhost:8000'


def nowa_reklama():
    return {
        'zrodlo': 'test',
        'id_zrodla': str(uuid.uuid4()),
        'platforma': 'facebook',
        'tekst': 'Zainwestuj 900 zł i zarabiaj 20 000 zł miesięcznie, zysk gwarantowany!',
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

    powtorka = httpx.post(f'{API}/reklamy', json=reklama, timeout=60)
    assert powtorka.status_code == 409

    lista = httpx.get(f'{API}/reklamy', params={'werdykt': 'oszustwo', 'min_ryzyko': 0.5}).json()
    assert zapisana['id'] in [r['id'] for r in lista]
    assert lista == sorted(lista, key=lambda r: r['ryzyko'], reverse=True)

    zmieniona = httpx.patch(f'{API}/reklamy/{zapisana["id"]}', json={'status': 'w_toku'})
    assert zmieniona.json()['status'] == 'w_toku'


def test_nieznana_reklama_daje_404():
    assert httpx.get(f'{API}/reklamy/0').status_code == 404


def test_progi_maja_liczby_dla_suwaka():
    progi = httpx.get(f'{API}/progi').json()
    assert progi['oszustw'] > 0 and progi['uczciwych'] > 0
    assert {'prog', 'zlapane', 'falszywe_alarmy'} <= set(progi['progi'][0])
