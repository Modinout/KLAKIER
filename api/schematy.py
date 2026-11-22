from datetime import date, datetime
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, model_validator

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
    notatka: str | None
    ma_obraz: bool
    poziom: Poziom
    powod: str | None

    @model_validator(mode='before')
    @classmethod
    def dolacz_sygnaly_i_poziom(cls, wiersz):
        # A row of the reklamy table keeps the collector's signals in their own column.
        sygnaly = wiersz['sygnaly_zbieracza'] + wiersz['sygnaly']
        poziom_reklamy, powod = poziom.poziom(sygnaly, wiersz['ponad_progiem'], wiersz['rodzaj'])
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
    notatka: str | None = None

    @model_validator(mode='after')
    def cos_zmienia(self):
        if not self.model_fields_set:
            raise ValueError('Podaj status, werdykt_analityka, domena albo notatka')
        return self


class WpisHistorii(BaseModel):
    kiedy: datetime
    kto: str
    co: str


class Prog(BaseModel):
    prog: float = Field(gt=0, lt=1)


class PowiazanaReklama(BaseModel):
    id: int
    tytul: str
    powod: Literal['ten_sam_telefon', 'ten_sam_komunikator']
    wartosc: str


class RejestracjaDomeny(BaseModel):
    zarejestrowano: date


class Domena(RejestracjaDomeny):
    domena: str
    sprawdzono: datetime


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


class OstrzezenieStrony(BaseModel):
    tekst: str
    px: float
    pogrubienie: float
    kontrast: float | None
    widoczne: bool
    bez_przewijania: bool


class WidokStrony(BaseModel):
    adres: str
    przewazajacy_px: float
    cfd: bool
    ostrzezenie: OstrzezenieStrony | None


class PomiarStrony(BaseModel):
    """A view is None when the page did not open in it."""

    komputer: WidokStrony | None
    telefon: WidokStrony | None


class Strona(PomiarStrony):
    domena: str
    zmierzono: datetime


class Obraz(BaseModel):
    obraz: str


class OdczytanyTekst(BaseModel):
    tekst: str


class Zlecenie(BaseModel):
    url: str

    @model_validator(mode='after')
    def adres_strony(self):
        self.url = self.url.strip()
        czesci = urlsplit(self.url)
        if czesci.scheme not in ('http', 'https') or not czesci.hostname:
            raise ValueError('Podaj adres strony zaczynający się od http:// albo https://')
        return self


class NoweSprawdzenie(BaseModel):
    id: int


class Sprawdzenie(BaseModel):
    stan: Literal['w_kolejce', 'w_toku', 'gotowe', 'blad']
    reklama_id: int | None = None
    blad: str | None = None


class NowyDowod(BaseModel):
    """One visit of a checked link: the screenshot as base64 PNG and the HTML of the page."""

    kiedy: datetime
    rodzaj: Literal['komputer', 'telefon']
    adres: str
    lancuch: list[str]
    obraz: str
    html: str


class Skroty(BaseModel):
    obraz: str
    html: str


class Dowod(BaseModel):
    id: int
    kiedy: datetime
    rodzaj: Literal['komputer', 'telefon']
    adres: str
    lancuch: list[str]
    sha256: Skroty
