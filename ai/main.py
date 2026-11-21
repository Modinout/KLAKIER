import csv
import pathlib
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import dopisane
import doradztwo
import drugi_sedzia
import duzy_model
import nowy_rodzaj
import ucz
import wymogi
from osadzenia import osadz
from przewidz import przeucz, przewidz, znane_rodzaje
from tekst import oczysc
from rejestr import sprawdz, sygnaly
from temat import platnik_do_sprawdzenia

PROGI = pathlib.Path(__file__).with_name('progi.csv')
# The classifier was trained and measured on ads. A video description is another kind of text, so it is not scored.
BEZ_OCENY = {'werdykt': 'ok', 'prawdopodobienstwa': {'oszustwo': 0.0}, 'pewny': True, 'powody': [], 'rodzaj': None}

app = FastAPI(title='KLAKIER AI')


class Material(BaseModel):
    tekst: str
    reklamodawca: str | None = None
    url: str | None = None
    zrodlo: str | None = None


@app.get('/zdrowie')
def zdrowie():
    return {'ok': True}


@app.post('/ocen')
def ocen(material: Material):
    wynik = BEZ_OCENY if material.zrodlo == 'youtube' else przewidz(material.tekst)
    rejestr = sprawdz(material.reklamodawca)
    na_temat = platnik_do_sprawdzenia(material.tekst, material.reklamodawca, rejestr)
    return {
        'werdykt': wynik['werdykt'],
        'ryzyko': wynik['prawdopodobienstwa']['oszustwo'],
        'pewny': wynik['pewny'],
        'powody': wynik['powody'],
        'rodzaj': wynik['rodzaj'],
        'rejestr': rejestr,
        'sygnaly': (
            (sygnaly(material.reklamodawca, rejestr, material.zrodlo) if na_temat else [])
            + wymogi.sygnaly(material.tekst, rejestr)
            + doradztwo.sygnaly(material.tekst, rejestr)
        ),
    }


class Tekst(BaseModel):
    tekst: str


class Przyklad(BaseModel):
    tekst: str
    werdykt: Literal['ok', 'do_sprawdzenia', 'oszustwo']


class Przyklady(BaseModel):
    przyklady: list[Przyklad]


class NowyRodzaj(BaseModel):
    nazwa: str
    opis: str


@app.post('/osadz')
def osadz_tekst(material: Tekst):
    return {'osadzenie': osadz(material.tekst)}


def _wymagaj_duzego_modelu():
    if not duzy_model.skonfigurowany():
        raise HTTPException(503, 'Duży model nie jest skonfigurowany.')


@app.post('/drugi_sedzia')
def ocen_drugim_sedzia(material: Tekst):
    _wymagaj_duzego_modelu()
    try:
        return drugi_sedzia.ocen(material.tekst)
    except Exception as blad:
        raise HTTPException(503, 'Duży model nie ocenił reklamy: ' + str(blad)) from blad


@app.post('/ucz')
def ucz_na_przykladach(zadanie: Przyklady):
    # Each call carries the analysts' whole set, so it replaces the one stored before.
    analityka = []
    for przyklad in zadanie.przyklady:
        tekst = oczysc(przyklad.tekst)
        if tekst.strip():
            analityka.append({'tekst': tekst, 'werdykt': przyklad.werdykt, 'rodzaj': None, 'pochodzenie': 'analityk'})
    dopisane.zapisz([w for w in dopisane.czytaj() if w['pochodzenie'] != 'analityk'] + analityka)
    przeucz()
    return {'przyklady': len(analityka), 'razem': len(ucz.wiersze())}


@app.get('/rodzaje')
def rodzaje():
    return znane_rodzaje()


@app.post('/rodzaje')
def dodaj_rodzaj(rodzaj: NowyRodzaj):
    if rodzaj.nazwa in znane_rodzaje():
        raise HTTPException(409, f'Rodzaj „{rodzaj.nazwa}” już jest znany.')
    _wymagaj_duzego_modelu()
    try:
        teksty = nowy_rodzaj.napisz(rodzaj.opis)
    except Exception as blad:
        raise HTTPException(503, 'Duży model nie napisał przykładów: ' + str(blad)) from blad
    nowy_rodzaj.dodaj(rodzaj.nazwa, teksty)
    return {'nazwa': rodzaj.nazwa, 'przyklady': len(teksty)}


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
