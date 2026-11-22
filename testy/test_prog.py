# Sprawdzenie zapisanego progu na działającym stosie: docker compose up, potem pytest testy.
import httpx
import pytest

from test_sciezka import API, nowa_reklama

# Model tekstowy uznaje to za oszustwo i nic poza tym nie jest ustaleniem, więc o poziomie decyduje tylko próg.
TEKST_MODELU = 'Nowa platforma daje 3 500 zł dziennie. Zarejestruj się dziś, liczba miejsc ograniczona.'


@pytest.fixture
def zapisany_prog():
    prog = httpx.get(f'{API}/prog').raise_for_status().json()['prog']
    yield prog
    httpx.put(f'{API}/prog', json={'prog': prog}).raise_for_status()


def poziom(numer):
    return httpx.get(f'{API}/reklamy/{numer}').json()['poziom']


def test_prog_ustala_poziom_reklamy_ocenionej_tylko_przez_model(zapisany_prog):
    reklama = httpx.post(f'{API}/reklamy', json=nowa_reklama(TEKST_MODELU), timeout=180).json()
    assert reklama['sygnaly'] == []
    # Tylko progi powyżej domyślnego, żeby inne reklamy w trakcie testu traciły alerty zamiast je zyskiwać.
    ponizej, powyzej = reklama['ryzyko'] - 0.001, (reklama['ryzyko'] + 1) / 2

    assert httpx.put(f'{API}/prog', json={'prog': ponizej}).json() == {'prog': ponizej}
    assert httpx.get(f'{API}/prog').json() == {'prog': ponizej}
    assert poziom(reklama['id']) == 'wysokie'

    httpx.put(f'{API}/prog', json={'prog': powyzej}).raise_for_status()
    assert httpx.get(f'{API}/prog').json() == {'prog': powyzej}
    assert poziom(reklama['id']) == 'niskie'


@pytest.mark.parametrize('prog', [0, 1, -0.2, 1.5])
def test_prog_spoza_przedzialu_daje_422(prog):
    assert httpx.put(f'{API}/prog', json={'prog': prog}).status_code == 422
