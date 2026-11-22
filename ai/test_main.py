# Test punktów końcowych usługi ai, duży model zastąpiony atrapami. Uruchom: docker compose run --rm ai python test_main.py
import json
import os
import sys

from fastapi.testclient import TestClient

import dopisane
import duzy_model
from main import app
from przewidz import przeucz

sys.stdout.reconfigure(encoding='utf-8')
for zmienna in ('DUZY_MODEL_URL', 'DUZY_MODEL_NAZWA', 'DUZY_MODEL_KLUCZ'):
    os.environ.pop(zmienna, None)
klient = TestClient(app)
liczba = zle = 0


def sprawdz(dobrze, *opis):
    global liczba, zle
    liczba += 1
    zle += not dobrze
    print('OK  ' if dobrze else 'FAIL', *opis)


REKLAMA = 'Zainwestuj 900 zł z Orlen i zarabiaj 20 000 zł miesięcznie! Gwarantowany dochód dla każdego Polaka.'
NOWY = {'nazwa': 'fałszywa loteria', 'opis': 'wygrana na loterii, którą odbiera się po wpłacie opłaty'}

odp = klient.post('/ocen', json={'tekst': REKLAMA, 'reklamodawca': None, 'url': None})
klucze = {'werdykt', 'ryzyko', 'pewny', 'sygnaly', 'powody', 'rodzaj'}
sprawdz(odp.status_code == 200 and klucze <= odp.json().keys(), '/ocen keys', sorted(odp.json()))
film = klient.post('/ocen', json={'tekst': REKLAMA, 'zrodlo': 'youtube'}).json()
sprawdz(film['werdykt'] == 'ok' and film['ryzyko'] == 0 and film['powody'] == [], 'a video description is not scored ->', film['werdykt'], film['ryzyko'])

wektor = klient.post('/osadz', json={'tekst': REKLAMA}).json()['osadzenie']
pusty = klient.post('/osadz', json={'tekst': ' '}).json()['osadzenie']
sprawdz(len(wektor) == 64 and pusty is None, '/osadz gives 64 numbers, none for an empty text ->', len(wektor), pusty)

odp = klient.post('/drugi_sedzia', json={'tekst': REKLAMA})
sprawdz(odp.status_code == 503, '/drugi_sedzia without a big model ->', odp.status_code, odp.json())
odp = klient.post('/rodzaje', json=NOWY)
sprawdz(odp.status_code == 503, 'POST /rodzaje without a big model ->', odp.status_code, odp.json())
odp = klient.get('/rodzaje')
sprawdz(len(odp.json()) == 4, 'GET /rodzaje', len(odp.json()), 'names')


def pisz_reklamy(prosba, temperature, max_tokens):
    # Przekręcony klucz, tak jak model czasem go pisze.
    return json.dumps({'rekalmy': [f'Wygrałeś {n} 000 zł w loterii! Odbierz nagrodę po wpłacie opłaty {n * 10} zł, zostało {n} godzin.'
                                   for n in range(1, 11)]}, ensure_ascii=False)


def oceniaj(prosba, temperature, max_tokens):
    return 'Oto ocena: {"werdykt": "oszustwo", "uzasadnienie": "Obiecuje nierealny zysk pod znaną marką."}'


bylo = dopisane.PLIK.exists()
przed = dopisane.czytaj()
try:
    duzy_model.skonfigurowany = lambda: True
    duzy_model.zapytaj = pisz_reklamy
    odp = klient.post('/rodzaje', json=NOWY)
    sprawdz(odp.status_code == 200 and odp.json()['przyklady'] == 20, 'POST /rodzaje ->', odp.status_code, odp.json())
    odp = klient.get('/rodzaje')
    sprawdz(len(odp.json()) == 5 and NOWY['nazwa'] in odp.json(), 'GET /rodzaje after adding', len(odp.json()), 'names')
    odp = klient.post('/ocen', json={'tekst': 'Wygrałeś w loterii 7 000 zł! Nagrodę odbierzesz po wpłacie opłaty.', 'reklamodawca': None, 'url': None})
    sprawdz(odp.json()['rodzaj'] == NOWY['nazwa'], '/ocen names the added type ->', odp.json()['rodzaj'])
    odp = klient.post('/rodzaje', json=NOWY)
    sprawdz(odp.status_code == 409, 'POST /rodzaje with a known name ->', odp.status_code)

    odp = klient.post('/ucz', json={'przyklady': [{'tekst': REKLAMA, 'werdykt': 'oszustwo'}, {'tekst': ' ', 'werdykt': 'ok'},
                                                  {'tekst': 'Kup akcje z prowizją 0 zł.', 'werdykt': 'do_sprawdzenia'}]})
    wynik = odp.json()
    sprawdz(odp.status_code == 200 and wynik['przyklady'] == 1 and type(wynik['razem']) is int and wynik['razem'] > 865,
            'POST /ucz learns only from ok and oszustwo ->', odp.status_code, wynik)

    duzy_model.zapytaj = oceniaj
    odp = klient.post('/drugi_sedzia', json={'tekst': REKLAMA})
    sprawdz(odp.status_code == 200 and odp.json()['werdykt'] == 'oszustwo', '/drugi_sedzia ->', odp.status_code, odp.json())
finally:
    if bylo:
        dopisane.zapisz(przed)
    else:
        dopisane.PLIK.unlink(missing_ok=True)
    przeucz()

odp = klient.get('/rodzaje')
sprawdz(len(odp.json()) == 4, 'GET /rodzaje after cleanup', len(odp.json()), 'names')
print('MAIN', liczba - zle, 'of', liczba, 'passed')
sys.exit(1 if zle else 0)
