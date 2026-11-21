import base64

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from czytaj import czytaj

app = FastAPI(title='KLAKIER odczyt')


class Obraz(BaseModel):
    obraz: str


@app.get('/zdrowie')
def zdrowie():
    return {'ok': True}


@app.post('/odczytaj')
def odczytaj(obraz: Obraz):
    try:
        return {'tekst': czytaj(base64.b64decode(obraz.obraz, validate=True))}
    except ValueError as blad:
        raise HTTPException(422, 'Nie udało się odczytać obrazu.') from blad
