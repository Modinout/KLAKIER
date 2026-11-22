# Check of ads linked by a shared contact on a running stack: docker compose up, then pytest testy.
import random
import sys
import uuid
from pathlib import Path

import httpx
import pytest

from test_sciezka import API, nowa_reklama

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'api'))

from kontakty import kontakty  # noqa: E402
from tytul import tytul  # noqa: E402


@pytest.mark.parametrize('tekst, numer', [
    ('Zadzwoń: +48 601 702 803', '+48601702803'),
    ('tel. 601-702-803.', '+48601702803'),
    ('Kontakt 601702803, odpisujemy szybko', '+48601702803'),
    ('Biuro: +48 22 522 23 90', '+48225222390'),
    ('Napisz na WhatsApp +39 333 145 4003!', '+393331454003'),
    ('contact +256705583377, +256703281533', '+256705583377'),
])
def test_numer_telefonu_jest_znormalizowany(tekst, numer):
    assert ('ten_sam_telefon', numer) in kontakty(tekst)


@pytest.mark.parametrize('tekst', [
    'Promocja trwa od 2026-11-21 12:00 do 21.11.2026 18:00.',
    'Zarobisz nawet 100 000 000 zł albo 250 000 000 PLN.',
    'NIP: 521-008-96-06, Regon: 011089780, KRS 0000123456',
    'https://finance.example/news/stocks-200666249 i finance.example/a-102959173.html?ha=530559531',
    'Telefon +48 512 345 678 albo 999 999 999',
])
def test_daty_kwoty_numery_firm_adresy_i_wzory_to_nie_telefony(tekst):
    assert {k for k in kontakty(tekst) if k[0] == 'ten_sam_telefon'} == set()


def test_komunikatory_sa_znormalizowane():
    tekst = ('Dołącz: https://t.me/ManiacyBiznesu, telegram.me/maniacybiznesu, t.me/+SuRn0iKffpE3ZWY0, '
             't.me/rarecryptosignals/980, wa.me/48601702803, https://api.whatsapp.com/send?phone=48601702804')
    assert kontakty(tekst) == {
        ('ten_sam_komunikator', 't.me/maniacybiznesu'),
        ('ten_sam_komunikator', 't.me/+SuRn0iKffpE3ZWY0'),
        ('ten_sam_komunikator', 't.me/rarecryptosignals'),
        ('ten_sam_komunikator', 'wa.me/48601702803'),
        ('ten_sam_komunikator', 'wa.me/48601702804'),
    }


def test_tytul_jak_w_panelu():
    bez_sygnalow = {'sygnaly': [], 'sygnaly_zbieracza': []}
    assert tytul({**bez_sygnalow, 'reklamodawca': 'Jan Kowalczyk', 'domena': 'www.zysk.example', 'url': None,
                  'tekst': ''}) == 'Jan Kowalczyk'
    assert tytul({**bez_sygnalow, 'reklamodawca': None, 'domena': 'www.zysk.example', 'url': None,
                  'tekst': ''}) == 'zysk.example'
    assert tytul({**bez_sygnalow, 'reklamodawca': None, 'domena': None,
                  'url': 'https://adstransparency.google.com/advertiser/AR1', 'tekst': 'Wejdź na www.Zysk.example dziś'}) == 'zysk.example'
    assert tytul({**bez_sygnalow, 'reklamodawca': None, 'domena': None, 'url': None, 'tekst': 'Bez adresu'}) == 'Reklama bez nadawcy'
    ostrzezona = {'kod': 'reklama_domeny_z_ostrzezenia_knf', 'opis': 'Domena zysk.example jest na liście ostrzeżeń KNF.'}
    assert tytul({'sygnaly': [], 'sygnaly_zbieracza': [ostrzezona], 'reklamodawca': 'Jan Kowalczyk', 'domena': None,
                  'url': None, 'tekst': ''}) == 'zysk.example'


def test_reklamy_ze_wspolnym_kontaktem_sa_powiazane():
    # Contacts unique to this run, so rows of earlier runs and real ads do not join in.
    cyfry = str(random.randrange(10**7, 10**8))
    numer = f'6{cyfry[:2]} {cyfry[2:5]} {cyfry[5:]}'
    kanal = 'kanal_' + uuid.uuid4().hex[:10]

    def dodaj(tekst, **pola):
        return httpx.post(f'{API}/reklamy', json={**nowa_reklama(tekst), **pola}, timeout=180).json()['id']

    pierwsza = dodaj(f'Zarabiaj z nami. Zadzwoń: +48 {numer} albo dołącz do t.me/{kanal}')
    telefon = dodaj(f'Kontakt: {numer.replace(" ", "-")}', reklamodawca='Jan Testowy')
    telegram = dodaj(f'Sygnały na https://t.me/{kanal.upper()}', domena='www.sygnaly.example')
    dodaj('Zarabiaj z nami, bez kontaktu.')

    powiazane = httpx.get(f'{API}/reklamy/{pierwsza}/powiazane').json()
    assert powiazane == [
        {'id': telefon, 'tytul': 'Jan Testowy', 'powod': 'ten_sam_telefon', 'wartosc': '+486' + cyfry},
        {'id': telegram, 'tytul': 'sygnaly.example', 'powod': 'ten_sam_komunikator', 'wartosc': f't.me/{kanal}'},
    ]
    assert [r['id'] for r in httpx.get(f'{API}/reklamy/{telefon}/powiazane').json()] == [pierwsza]


def test_powiazane_nieznanej_reklamy_daje_404():
    odpowiedz = httpx.get(f'{API}/reklamy/0/powiazane')
    assert odpowiedz.status_code == 404
    assert odpowiedz.json()['detail'] == 'Nie ma takiej reklamy'
