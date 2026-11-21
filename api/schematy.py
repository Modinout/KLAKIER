from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, model_validator

import poziom

Werdykt = Literal['ok', 'do_sprawdzenia', 'oszustwo']
Status = Literal['nowa', 'w_toku', 'zamknieta']
Poziom = Literal['wysokie', 'srednie', 'niskie']


class Sygnal(BaseModel):
    modul: str
    kod: str
    opis: str
    podstawa: str = ''


class Powod(BaseModel):
    slowo: str
    waga: float


class DrugiSedzia(BaseModel):
    werdykt: Werdykt
    uzasadnienie: str


class Rejestr(BaseModel):
    stan: Literal['w_rejestrze', 'spoza_rejestru', 'tfi', 'bank', 'poza_listami']
    podmiot: str | None
    panstwo: str | None
    lista: str | None


class NowaReklama(BaseModel):
    zrodlo: str
    id_zrodla: str
    platforma: str
    url: str | None = None
    domena: str | None = None
    reklamodawca: str | None = None
    tekst: str
    zebrano: datetime
    opublikowano: date | None = None
    sygnaly: list[Sygnal] = []


class Reklama(NowaReklama):
    id: int
    dodano: datetime
    werdykt: Werdykt
    ryzyko: float
    pewny: bool
    rejestr: Rejestr | None
    sygnaly: list[Sygnal]
    powody: list[Powod]
    rodzaj: str | None
    drugi_sedzia: DrugiSedzia | None
    status: Status
    werdykt_analityka: Werdykt | None
    ma_obraz: bool
    poziom: Poziom
    powod: str | None

    @model_validator(mode='before')
    @classmethod
    def dolacz_sygnaly_i_poziom(cls, wiersz):
        # A row of the reklamy table keeps the collector's signals in their own column.
        sygnaly = wiersz['sygnaly_zbieracza'] + wiersz['sygnaly']
        poziom_reklamy, powod = poziom.poziom(sygnaly, wiersz['werdykt'], wiersz['rodzaj'])
        return {**wiersz, 'sygnaly': sygnaly, 'poziom': poziom_reklamy, 'powod': powod}


class PodobnaReklama(Reklama):
    podobienstwo: float


class Alert(BaseModel):
    id: int
    reklamodawca: str | None
    ryzyko: float
    werdykt: Werdykt
    zrodlo: str
    dodano: datetime
    poziom: Poziom
    powod: str | None


class ZmianaReklamy(BaseModel):
    """Only the fields sent are changed, so the default None of status is never stored."""

    status: Status = None
    werdykt_analityka: Werdykt | None = None
    domena: str | None = None

    @model_validator(mode='after')
    def cos_zmienia(self):
        if not self.model_fields_set:
            raise ValueError('Podaj status, werdykt_analityka albo domena')
        return self


class NowyRodzaj(BaseModel):
    nazwa: str
    opis: str


class DodanyRodzaj(BaseModel):
    nazwa: str
    przyklady: int
    przeliczono: int


class Nauka(BaseModel):
    przyklady: int
    przeliczono: int


class Obraz(BaseModel):
    obraz: str


class OdczytanyTekst(BaseModel):
    tekst: str
