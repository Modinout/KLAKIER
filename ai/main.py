import csv
import pathlib

from fastapi import FastAPI
from pydantic import BaseModel

from przewidz import przewidz

PROGI = pathlib.Path(__file__).with_name('progi.csv')

app = FastAPI(title='KLAKIER AI')


class Material(BaseModel):
    tekst: str
    reklamodawca: str | None = None
    url: str | None = None


@app.get('/zdrowie')
def zdrowie():
    return {'ok': True}


@app.post('/ocen')
def ocen(material: Material):
    wynik = przewidz(material.tekst)
    return {
        'werdykt': wynik['werdykt'],
        'ryzyko': wynik['prawdopodobienstwa']['oszustwo'],
        'pewny': wynik['pewny'],
        # Modules M1-M3 (KNF registers, UKNF risk rules, unlicensed advice) add their findings here.
        'sygnaly': [],
    }


@app.get('/progi')
def progi():
    with PROGI.open(encoding='utf-8') as plik:
        naglowek, *wiersze = csv.reader(plik, delimiter=';')
    # The header names end with the test set sizes: oszustwa_zlapane_z_30, falszywe_alarmy_z_177.
    return {
        'oszustw': int(naglowek[1].rsplit('_', 1)[1]),
        'uczciwych': int(naglowek[2].rsplit('_', 1)[1]),
        'progi': [{'prog': float(w[0]), 'zlapane': float(w[1]), 'falszywe_alarmy': float(w[2])} for w in wiersze],
    }
