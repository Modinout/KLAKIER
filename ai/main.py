import csv
import pathlib
import threading
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import dopisane
import doradztwo
import drugi_sedzia
import duzy_model
import nowy_rodzaj
import polecenia
import ucz
import wymogi
from osadzenia import osadz
from przewidz import przeucz, przewidz, znane_rodzaje
from tekst import oczysc
from rejestr import sprawdz, sygnaly
from temat import platnik_do_sprawdzenia

PROGI = pathlib.Path(__file__).with_name('progi.csv')
# Klasyfikator uczono i mierzono na reklamach. Opis filmu to inny rodzaj tekstu, więc nie jest oceniany.
BEZ_OCENY = {'werdykt': 'ok', 'prawdopodobienstwa': {'oszustwo': 0.0}, 'pewny': True, 'powody': [], 'rodzaj': None}
# Dwa jednoczesne douczania nadpisałyby sobie nawzajem plik z przykładami.
_uczenie = threading.Lock()

app = FastAPI(title='KLAKIER AI')


class Material(BaseModel):
    tekst: str
    reklamodawca: str | None = None
    url: str | None = None
    zrodlo: str | None = None
    mowa: str | None = None


@app.get('/zdrowie')
def zdrowie():
    return {'ok': True}


@app.post('/ocen')
def ocen(material: Material):
    # Mowa z nagrania reklamy mówi to samo co tekst posta, więc model i reguły czytają oba razem.
    # Linki polecające są tylko w tekście opisu.
    tekst = '\n'.join(filter(None, [material.tekst, material.mowa]))
    wynik = BEZ_OCENY if material.zrodlo == 'youtube' else przewidz(tekst)
    # Mowa, której model nie zna (na przykład po angielsku), nie może rozmyć ryzyka samego tekstu.
    if material.mowa and material.zrodlo != 'youtube':
        wynik = max(wynik, przewidz(material.tekst), key=lambda w: w['prawdopodobienstwa']['oszustwo'])
    rejestr = sprawdz(material.reklamodawca)
    na_temat = platnik_do_sprawdzenia(tekst, material.reklamodawca, rejestr)
    return {
        'werdykt': wynik['werdykt'],
        'ryzyko': wynik['prawdopodobienstwa']['oszustwo'],
        'pewny': wynik['pewny'],
        'powody': wynik['powody'],
        'rodzaj': wynik['rodzaj'],
        'rejestr': rejestr,
        'sygnaly': (
            (sygnaly(material.reklamodawca, rejestr, material.zrodlo) if na_temat else [])
            + wymogi.sygnaly(tekst, rejestr, material.zrodlo)
            + doradztwo.sygnaly(tekst, rejestr)
            + polecenia.sygnaly(material.tekst, rejestr, material.zrodlo)
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
    # Każde wywołanie niesie cały zestaw analityków, więc zastępuje ten zapisany wcześniej.
    # Reklama zostawiona do sprawdzenia nie ma jeszcze werdyktu, a model nauczyłby się jej jako nie-oszustwa.
    analityka = []
    for przyklad in zadanie.przyklady:
        tekst = oczysc(przyklad.tekst)
        if tekst.strip() and przyklad.werdykt != 'do_sprawdzenia':
            analityka.append({'tekst': tekst, 'werdykt': przyklad.werdykt, 'rodzaj': None, 'pochodzenie': 'analityk'})
    with _uczenie:
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
    # Nazwy w nagłówku kończą się rozmiarami zbioru testowego: oszustwa_zlapane_z_30, falszywe_alarmy_z_177.
    return {
        'oszustw': int(naglowek[1].rsplit('_', 1)[1]),
        'uczciwych': int(naglowek[2].rsplit('_', 1)[1]),
        'progi': [{'prog': float(w[0]), 'zlapane': float(w[1]), 'falszywe_alarmy': float(w[2])} for w in wiersze],
    }
