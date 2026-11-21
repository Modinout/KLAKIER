from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Werdykt = Literal['ok', 'do_sprawdzenia', 'oszustwo']
Status = Literal['nowa', 'w_toku', 'zamknieta']


class Sygnal(BaseModel):
    modul: str
    kod: str
    opis: str
    podstawa: str = ''


class NowaReklama(BaseModel):
    zrodlo: str
    id_zrodla: str
    platforma: str
    url: str | None = None
    reklamodawca: str | None = None
    tekst: str
    zebrano: datetime


class Reklama(NowaReklama):
    id: int
    dodano: datetime
    werdykt: Werdykt
    ryzyko: float
    pewny: bool
    sygnaly: list[Sygnal]
    status: Status


class ZmianaStatusu(BaseModel):
    status: Status
