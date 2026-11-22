# Link wklejony w panelu, na działającym stosie: robotnik go otwiera, api go przechowuje.
# Wymaga internetu, bo robotnik odmawia otwierania własnych adresów stosu.
import hashlib
import io
import json
import subprocess
import time
import zipfile
from pathlib import Path

import httpx
import pytest

from test_sciezka import API

REPO = Path(__file__).resolve().parent.parent
STRONA = 'https://example.com/'


def psql(polecenie):
    """Wynik jednego polecenia SQL w żywej bazie, bez nagłówków."""
    return subprocess.run(
        ['docker', 'compose', 'exec', '-T', 'baza', 'psql', '-U', 'klakier', '-d', 'klakier', '-tAc', polecenie],
        cwd=REPO, check=True, capture_output=True, text=True,
    ).stdout.strip()


@pytest.fixture
def numery():
    """Id sprawdzeń zakolejkowanych przez test; ich wiersze, rekordy, dowody i pomiar strony znikają po teście."""
    numery = []
    yield numery
    # Po linku: przerwane sprawdzenie może zostawić rekord, na który nie wskazuje jego wiersz.
    psql("DELETE FROM reklamy WHERE zrodlo = 'panel' AND id_zrodla LIKE 'https://example.com/%'")
    if numery:
        psql(f'DELETE FROM sprawdzenia WHERE id IN ({",".join(map(str, numery))})')
    psql("DELETE FROM strony WHERE domena = 'example.com'")


def zlec(url, numery):
    """Kolejkuje link i czeka na robotnika, który może najpierw dokończyć domenę patrolu; zwraca stan końcowy."""
    zlecone = httpx.post(f'{API}/sprawdz', json={'url': url}, timeout=30)
    assert zlecone.status_code == 202
    numery.append(zlecone.json()['id'])
    koniec = time.monotonic() + 600
    while time.monotonic() < koniec:
        stan = httpx.get(f'{API}/sprawdz/{numery[-1]}').json()
        if stan['stan'] in ('gotowe', 'blad'):
            return stan
        time.sleep(2)
    raise AssertionError(f'Sprawdzenie {numery[-1]} trwa ponad 10 minut: {stan}')


def test_link_daje_reklame_z_dowodami_z_obu_widokow(numery):
    stan = zlec(STRONA, numery)
    assert stan['stan'] == 'gotowe' and stan['blad'] is None
    reklama = httpx.get(f'{API}/reklamy/{stan["reklama_id"]}').json()
    assert (reklama['zrodlo'], reklama['url'], reklama['domena'], reklama['ma_obraz']) == (
        'panel', STRONA, 'example.com', True)
    assert 'Example Domain' in reklama['tekst']
    assert psql("SELECT count(*) FROM strony WHERE domena = 'example.com'") == '1'

    pierwsze = httpx.get(f'{API}/reklamy/{reklama["id"]}/dowody').json()
    assert [dowod['rodzaj'] for dowod in pierwsze] == ['komputer', 'telefon']
    for dowod in pierwsze:
        assert dowod['lancuch'] == [STRONA] and dowod['adres'] == STRONA
        obraz = httpx.get(f'{API}/dowody/{dowod["id"]}/obraz')
        assert obraz.headers['content-type'] == 'image/png'
        assert hashlib.sha256(obraz.content).hexdigest() == dowod['sha256']['obraz']
        html = httpx.get(f'{API}/dowody/{dowod["id"]}/html')
        assert html.headers['content-type'] == 'text/plain; charset=utf-8'
        assert html.headers['content-disposition'].startswith('attachment')
        assert hashlib.sha256(html.content).hexdigest() == dowod['sha256']['html']
    komputer = httpx.get(f'{API}/dowody/{pierwsze[0]["id"]}/obraz').content
    assert httpx.get(f'{API}/reklamy/{reklama["id"]}/obraz').content == komputer

    # Drugie sprawdzenie tego samego linku dodaje jego wizyty do tego samego rekordu i zachowuje wcześniejsze.
    assert zlec(STRONA, numery)['reklama_id'] == reklama['id']
    wszystkie = httpx.get(f'{API}/reklamy/{reklama["id"]}/dowody').json()
    assert wszystkie[:2] == pierwsze
    assert [dowod['rodzaj'] for dowod in wszystkie[2:]] == ['komputer', 'telefon']

    paczka = httpx.get(f'{API}/reklamy/{reklama["id"]}/paczka')
    assert paczka.headers['content-type'] == 'application/zip'
    with zipfile.ZipFile(io.BytesIO(paczka.content)) as archiwum:
        manifest = json.loads(archiwum.read('manifest.json'))
        assert manifest['url'] == STRONA and [dowod['id'] for dowod in manifest['dowody']] == [d['id'] for d in wszystkie]
        for dowod, zapisany in zip(manifest['dowody'], wszystkie):
            skroty = [hashlib.sha256(archiwum.read(plik['plik'])).hexdigest() for plik in dowod['pliki']]
            assert skroty == [plik['sha256'] for plik in dowod['pliki']]
            assert skroty == [zapisany['sha256']['obraz'], zapisany['sha256']['html']]


def test_strona_z_kodem_bledu_nie_daje_reklamy(numery):
    url = 'https://example.com/nie-ma-takiej-strony'
    assert zlec(url, numery) == {'stan': 'blad', 'reklama_id': None, 'blad': 'Strona odpowiedziała kodem błędu 404.'}
    assert psql(f"SELECT count(*) FROM reklamy WHERE zrodlo = 'panel' AND id_zrodla = '{url}'") == '0'


def test_adres_bez_http_daje_422():
    assert httpx.post(f'{API}/sprawdz', json={'url': 'zla.example/oferta'}).status_code == 422


def test_adres_sieci_wewnetrznej_daje_422():
    for url in ('http://api:8000/zdrowie', 'http://localhost:8000/', 'http://127.0.0.1:8000/', 'http://[::1]/',
                'http://169.254.169.254/latest/meta-data/', 'http://host.docker.internal:8000/'):
        assert httpx.post(f'{API}/sprawdz', json={'url': url}).status_code == 422, url


def test_nieznane_sprawdzenie_i_dowod_daja_404():
    assert httpx.get(f'{API}/sprawdz/0').status_code == 404
    assert httpx.get(f'{API}/reklamy/0/dowody').status_code == 404
    assert httpx.get(f'{API}/dowody/0/obraz').status_code == 404
    assert httpx.get(f'{API}/dowody/0/html').status_code == 404
    assert httpx.get(f'{API}/reklamy/0/paczka').status_code == 404
