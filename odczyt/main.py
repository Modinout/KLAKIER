import base64

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from czytaj import czytaj
from sluchaj import sluchaj

app = FastAPI(title='KLAKIER odczyt')


class Obraz(BaseModel):
    obraz: str


class Nagranie(BaseModel):
    nagranie: str


@app.get('/zdrowie')
def zdrowie():
    return {'ok': True}


@app.post('/odczytaj')
def odczytaj(obraz: Obraz):
    try:
        return {'tekst': czytaj(base64.b64decode(obraz.obraz, validate=True))}
    except ValueError as blad:
        raise HTTPException(422, 'Nie udało się odczytać obrazu.') from blad
    except Exception as blad:
        raise HTTPException(500, 'Odczyt obrazu się nie powiódł.') from blad


@app.post('/posluchaj')
def posluchaj(nagranie: Nagranie):
    try:
        return {'tekst': sluchaj(base64.b64decode(nagranie.nagranie, validate=True))}
    except ValueError as blad:
        raise HTTPException(422, 'Nie udało się odczytać nagrania.') from blad
    except Exception as blad:
        raise HTTPException(500, 'Zamiana mowy na tekst się nie powiodła.') from blad
