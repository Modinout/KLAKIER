# Wyszukiwania w bibliotece reklam TikToka zlecane z panelu: api kolejkuje frazę, a robotnik zapisuje w kolejce, jak poszło.
import json

import redis
from fastapi import APIRouter, HTTPException

from schematy import Fraza, NoweSprawdzenie, Wyszukiwanie
from sprawdzenia import KOLEJKA

# Robotnik bierze tę listę po linkach, a przed domenami patrolu (zbieracz/kolejka.py).
FRAZY = 'patrol:frazy'
NUMER = 'patrol:numer'
OSTATNIE = 'patrol:ostatnie'

router = APIRouter()


def klucz(id):
    return f'patrol:wyszukiwanie:{id}'


@router.post('/patrol', response_model=NoweSprawdzenie, status_code=202, summary='Zleć wyszukiwanie frazy w bibliotece TikToka',
             tags=['Patrol'])
def zlec(zlecenie: Fraza):
    try:
        id = KOLEJKA.incr(NUMER)
        KOLEJKA.set(klucz(id), json.dumps({'fraza': zlecenie.fraza, 'stan': 'w_kolejce'}))
        KOLEJKA.rpush(FRAZY, json.dumps({'id': id, 'fraza': zlecenie.fraza}))
    except redis.RedisError as blad:
        raise HTTPException(503, 'Kolejka patrolu nie działa.') from blad
    return {'id': id}


@router.get('/patrol', response_model=Wyszukiwanie | None, summary='Ostatnie zakończone wyszukiwanie', tags=['Patrol'])
def ostatnie():
    return odczytane(OSTATNIE)


@router.get('/patrol/{id}', response_model=Wyszukiwanie, summary='Stan wyszukiwania', tags=['Patrol'])
def stan(id: int):
    wyszukiwanie = odczytane(klucz(id))
    if wyszukiwanie is None:
        raise HTTPException(404, 'Nie ma takiego wyszukiwania')
    return wyszukiwanie


def odczytane(nazwa):
    try:
        zapis = KOLEJKA.get(nazwa)
    except redis.RedisError as blad:
        raise HTTPException(503, 'Kolejka patrolu nie działa.') from blad
    return json.loads(zapis) if zapis else None
