# A link pasted in the panel, on a running stack with the patrol profile: the robotnik opens it, the api keeps it.
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
# Reachable from the robotnik without the internet; the api answers the trailing slash with a redirect.
STRONA = 'http://api:8000/zdrowie/'
KONIEC_STRONY = 'http://api:8000/zdrowie'


def psql(polecenie):
    """Output of one SQL command in the live base, without headers."""
    return subprocess.run(
        ['docker', 'compose', 'exec', '-T', 'baza', 'psql', '-U', 'klakier', '-d', 'klakier', '-tAc', polecenie],
        cwd=REPO, check=True, capture_output=True, text=True,
    ).stdout.strip()


@pytest.fixture
def numery():
    """Ids of the checks a test queued; their rows, records, evidence and page measurement go after the test."""
    numery = []
    yield numery
    # By the link: a check cut short can leave a record its row does not point to.
    psql("DELETE FROM reklamy WHERE zrodlo = 'panel' AND id_zrodla LIKE 'http://api:8000/%'")
    if numery:
        psql(f'DELETE FROM sprawdzenia WHERE id IN ({",".join(map(str, numery))})')
    psql("DELETE FROM strony WHERE domena = 'api'")


def zlec(url, numery):
    """Queues the link and waits for the robotnik, which may first finish a patrol domain; returns the final state."""
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
    assert (reklama['zrodlo'], reklama['url'], reklama['domena'], reklama['ma_obraz']) == ('panel', STRONA, 'api', True)
    assert 'ok' in reklama['tekst']
    assert psql("SELECT count(*) FROM strony WHERE domena = 'api'") == '1'

    pierwsze = httpx.get(f'{API}/reklamy/{reklama["id"]}/dowody').json()
    assert [dowod['rodzaj'] for dowod in pierwsze] == ['komputer', 'telefon']
    for dowod in pierwsze:
        assert dowod['lancuch'] == [STRONA, KONIEC_STRONY] and dowod['adres'] == KONIEC_STRONY
        obraz = httpx.get(f'{API}/dowody/{dowod["id"]}/obraz')
        assert obraz.headers['content-type'] == 'image/png'
        assert hashlib.sha256(obraz.content).hexdigest() == dowod['sha256']['obraz']
        html = httpx.get(f'{API}/dowody/{dowod["id"]}/html')
        assert html.headers['content-type'] == 'text/plain; charset=utf-8'
        assert html.headers['content-disposition'].startswith('attachment')
        assert hashlib.sha256(html.content).hexdigest() == dowod['sha256']['html']
    komputer = httpx.get(f'{API}/dowody/{pierwsze[0]["id"]}/obraz').content
    assert httpx.get(f'{API}/reklamy/{reklama["id"]}/obraz').content == komputer

    # A second check of the same link adds its visits to the same record and keeps the earlier ones.
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
    url = 'http://api:8000/nie-ma-takiej-strony'
    assert zlec(url, numery) == {'stan': 'blad', 'reklama_id': None, 'blad': 'Strona odpowiedziała kodem błędu 404.'}
    assert psql(f"SELECT count(*) FROM reklamy WHERE zrodlo = 'panel' AND id_zrodla = '{url}'") == '0'


def test_adres_bez_http_daje_422():
    assert httpx.post(f'{API}/sprawdz', json={'url': 'zla.example/oferta'}).status_code == 422


def test_nieznane_sprawdzenie_i_dowod_daja_404():
    assert httpx.get(f'{API}/sprawdz/0').status_code == 404
    assert httpx.get(f'{API}/reklamy/0/dowody').status_code == 404
    assert httpx.get(f'{API}/dowody/0/obraz').status_code == 404
    assert httpx.get(f'{API}/dowody/0/html').status_code == 404
    assert httpx.get(f'{API}/reklamy/0/paczka').status_code == 404
