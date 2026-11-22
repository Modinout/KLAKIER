# Test punktów końcowych usługi ai. Uruchom: docker compose run --rm ai python test_main.py
import sys

from fastapi.testclient import TestClient

import dopisane
from main import app
from przewidz import przeucz

sys.stdout.reconfigure(encoding='utf-8')
klient = TestClient(app)
liczba = zle = 0


def sprawdz(dobrze, *opis):
    global liczba, zle
    liczba += 1
    zle += not dobrze
    print('OK  ' if dobrze else 'FAIL', *opis)


REKLAMA = 'Zainwestuj 900 zł z Orlen i zarabiaj 20 000 zł miesięcznie! Gwarantowany dochód dla każdego Polaka.'

odp = klient.post('/ocen', json={'tekst': REKLAMA, 'reklamodawca': None, 'url': None})
klucze = {'werdykt', 'ryzyko', 'pewny', 'sygnaly', 'powody', 'rodzaj'}
sprawdz(odp.status_code == 200 and klucze <= odp.json().keys(), '/ocen keys', sorted(odp.json()))
film = klient.post('/ocen', json={'tekst': REKLAMA, 'zrodlo': 'youtube'}).json()
sprawdz(film['werdykt'] == 'ok' and film['ryzyko'] == 0 and film['powody'] == [], 'a video description is not scored ->', film['werdykt'], film['ryzyko'])

wektor = klient.post('/osadz', json={'tekst': REKLAMA}).json()['osadzenie']
pusty = klient.post('/osadz', json={'tekst': ' '}).json()['osadzenie']
sprawdz(len(wektor) == 64 and pusty is None, '/osadz gives 64 numbers, none for an empty text ->', len(wektor), pusty)

odp = klient.get('/rodzaje')
sprawdz(len(odp.json()) == 4, 'GET /rodzaje', len(odp.json()), 'names')
for usunieta in ('/drugi_sedzia', '/rodzaje'):
    odp = klient.post(usunieta, json={'tekst': REKLAMA})
    sprawdz(odp.status_code in (404, 405), 'POST', usunieta, 'is gone ->', odp.status_code)

bylo = dopisane.PLIK.exists()
przed = dopisane.czytaj()
try:
    odp = klient.post('/ucz', json={'przyklady': [{'tekst': REKLAMA, 'werdykt': 'oszustwo'}, {'tekst': ' ', 'werdykt': 'ok'},
                                                  {'tekst': 'Kup akcje z prowizją 0 zł.', 'werdykt': 'do_sprawdzenia'}]})
    wynik = odp.json()
    sprawdz(odp.status_code == 200 and wynik['przyklady'] == 1 and type(wynik['razem']) is int and wynik['razem'] > 1000,
            'POST /ucz learns only from ok and oszustwo ->', odp.status_code, wynik)
finally:
    if bylo:
        dopisane.zapisz(przed)
    else:
        dopisane.PLIK.unlink(missing_ok=True)
    przeucz()

# Niewinny tekst posta, a oszustwo w mowie nagrania: ocena ma wziąć pod uwagę mowę.
post = {'tekst': 'Zobacz nasz nowy film.', 'reklamodawca': 'Nieznana Sp. z o.o.', 'zrodlo': 'meta_ads'}
bez_mowy = klient.post('/ocen', json=post).json()
z_mowa = klient.post('/ocen', json={**post, 'mowa': 'Zainwestuj 900 zł z Orlenem i zarabiaj 20 000 zł miesięcznie, gwarantowany dochód.'}).json()
sprawdz(bez_mowy['werdykt'] != 'oszustwo' and z_mowa['werdykt'] == 'oszustwo', 'speech in the recording changes the verdict ->',
        bez_mowy['werdykt'], z_mowa['werdykt'])
oszustwo = {**post, 'tekst': 'Zainwestuj 900 zł z Orlenem i zarabiaj 20 000 zł miesięcznie, gwarantowany dochód.'}
sam_tekst = klient.post('/ocen', json=oszustwo).json()['ryzyko']
z_obca_mowa = klient.post('/ocen', json={**oszustwo, 'mowa': 'Thanks for watching, see you next week.'}).json()['ryzyko']
sprawdz(z_obca_mowa >= sam_tekst, 'unrelated speech does not lower the text risk ->', round(sam_tekst, 2), round(z_obca_mowa, 2))
print('MAIN', liczba - zle, 'of', liczba, 'passed')
sys.exit(1 if zle else 0)
