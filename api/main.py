import os

import httpx
from fastapi import FastAPI, HTTPException

import baza
from schematy import NowaReklama, Reklama, Status, Werdykt, ZmianaStatusu

AI_URL = os.environ['AI_URL']

app = FastAPI(title='KLAKIER API')


@app.get('/zdrowie')
def zdrowie():
    return {'ok': True}


@app.post('/reklamy', response_model=Reklama, status_code=201)
def dodaj_reklame(reklama: NowaReklama):
    ocena = httpx.post(f'{AI_URL}/ocen', json=reklama.model_dump(mode='json'), timeout=60).raise_for_status().json()
    wiersz = baza.dodaj(reklama.model_dump(), ocena)
    if wiersz is None:
        raise HTTPException(409, 'Ta reklama jest już w bazie')
    return wiersz


@app.get('/reklamy', response_model=list[Reklama])
def lista_reklam(werdykt: Werdykt | None = None, status: Status | None = None, min_ryzyko: float = 0):
    return baza.lista(werdykt, status, min_ryzyko)


@app.get('/reklamy/{id}', response_model=Reklama)
def jedna_reklama(id: int):
    return znaleziona(baza.jedna(id))


@app.patch('/reklamy/{id}', response_model=Reklama)
def zmien_status(id: int, zmiana: ZmianaStatusu):
    return znaleziona(baza.zmien_status(id, zmiana.status))


@app.get('/progi')
def progi():
    return httpx.get(f'{AI_URL}/progi', timeout=10).raise_for_status().json()


def znaleziona(wiersz):
    if wiersz is None:
        raise HTTPException(404, 'Nie ma takiej reklamy')
    return wiersz
