# Links an analyst pastes in the panel: the api queues them and the robotnik reports back how each check went.
import json
import os

import redis
from fastapi import APIRouter, HTTPException

import baza
from schematy import NoweSprawdzenie, Sprawdzenie, Zlecenie

# The robotnik takes this list before the patrol's domains (zbieracz/kolejka.py).
LINKI = 'patrol:linki'
KOLEJKA = redis.Redis.from_url(os.environ['KOLEJKA_URL'])

router = APIRouter()


@router.post('/sprawdz', response_model=NoweSprawdzenie, status_code=202)
def zlec(zlecenie: Zlecenie):
    id = baza.dodaj_sprawdzenie(zlecenie.url)
    try:
        KOLEJKA.rpush(LINKI, json.dumps({'id': id, 'url': zlecenie.url}))
    except redis.RedisError as blad:
        baza.usun_sprawdzenie(id)
        raise HTTPException(503, 'Kolejka sprawdzeń nie działa.') from blad
    return {'id': id}


@router.get('/sprawdz/{id}', response_model=Sprawdzenie)
def stan(id: int):
    return znalezione(baza.sprawdzenie(id))


@router.put('/sprawdz/{id}', response_model=Sprawdzenie)
def zapisz_stan(id: int, sprawdzenie: Sprawdzenie):
    """The robotnik reports here how the check goes."""
    return znalezione(baza.zapisz_sprawdzenie(id, sprawdzenie.model_dump()))


def znalezione(wiersz):
    if wiersz is None:
        raise HTTPException(404, 'Nie ma takiego sprawdzenia')
    return wiersz
