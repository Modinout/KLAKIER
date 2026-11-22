# Linki wklejane przez analityka w panelu: api kolejkuje je, a robotnik zgłasza, jak poszło każde sprawdzenie.
import json
import os

import redis
from fastapi import APIRouter, HTTPException

import baza
from schematy import NoweSprawdzenie, Sprawdzenie, Zlecenie

# Robotnik bierze tę listę przed domenami patrolu (zbieracz/kolejka.py).
LINKI = 'patrol:linki'
KOLEJKA = redis.Redis.from_url(os.environ['KOLEJKA_URL'])

router = APIRouter()


@router.post('/sprawdz', response_model=NoweSprawdzenie, status_code=202, summary='Zleć sprawdzenie linku',
             tags=['Sprawdzanie linków'])
def zlec(zlecenie: Zlecenie):
    id = baza.dodaj_sprawdzenie(zlecenie.url)
    try:
        KOLEJKA.rpush(LINKI, json.dumps({'id': id, 'url': zlecenie.url}))
    except redis.RedisError as blad:
        baza.usun_sprawdzenie(id)
        raise HTTPException(503, 'Kolejka sprawdzeń nie działa.') from blad
    return {'id': id}


@router.get('/sprawdz/{id}', response_model=Sprawdzenie, summary='Stan sprawdzenia linku',
            tags=['Sprawdzanie linków'])
def stan(id: int):
    return znalezione(baza.sprawdzenie(id))


@router.put('/sprawdz/{id}', response_model=Sprawdzenie, summary='Zapisz stan sprawdzenia',
            tags=['Dla zbieraczy'])
def zapisz_stan(id: int, sprawdzenie: Sprawdzenie):
    """Robotnik zgłasza tu, jak idzie sprawdzenie."""
    return znalezione(baza.zapisz_sprawdzenie(id, sprawdzenie.model_dump()))


def znalezione(wiersz):
    if wiersz is None:
        raise HTTPException(404, 'Nie ma takiego sprawdzenia')
    return wiersz
