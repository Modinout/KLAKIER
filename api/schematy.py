import ipaddress
from datetime import date, datetime
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, model_validator

import poziom

Werdykt = Literal['ok', 'do_sprawdzenia', 'oszustwo']
Status = Literal['nowa', 'w_toku', 'zamknieta']
Poziom = Literal['wysokie', 'srednie', 'niskie']


class Firma(BaseModel):
    nazwa: str
    domena: str
    stan_rejestru: str | None


class Sygnal(BaseModel):
    modul: str
    kod: str
    opis: str
    podstawa: str = ''
    # Tylko przy poleceniu z linkiem: polecana firma i jej stan w rejestrach.
    firma: Firma | None = None


class Powod(BaseModel):
    slowo: str
    waga: float


class DrugiSedzia(BaseModel):
    werdykt: Werdykt
    uzasadnienie: str


class Rejestr(BaseModel):
    stan: Literal['w_rejestrze', 'spoza_rejestru', 'tfi', 'bank', 'mica', 'poza_listami']
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
        # Wiersz tabeli reklamy trzyma sygnały zbieracza we własnej kolumnie.
        sygnaly = wiersz['sygnaly_zbieracza'] + wiersz['sygnaly']
        poziom_reklamy, powod = poziom.poziom(sygnaly, wiersz['ponad_progiem'], wiersz['rodzaj'], wiersz['rejestr'])
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
    """Zmieniane są tylko przesłane pola, więc domyślne None w status nigdy nie jest zapisywane."""

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
    """Widok jest None, gdy strona w nim się nie otworzyła."""

    komputer: WidokStrony | None
    # Sprawdzenie linku z panelu mierzy tylko komputer i telefon.
    tablet: WidokStrony | None = None
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
        if adres_wewnetrzny(czesci.hostname):
            raise ValueError('Link prowadzi do adresu w sieci wewnętrznej, a sprawdzamy tylko strony w internecie.')
        return self


def adres_wewnetrzny(host):
    """Host sieci lokalnej; nazwy wymagające DNS robotnik sprawdza ponownie, zanim je otworzy."""
    try:
        return not ipaddress.ip_address(host).is_global
    except ValueError:
        return '.' not in host or host.endswith(('.local', '.internal', '.localhost'))


class NoweSprawdzenie(BaseModel):
    id: int


class Sprawdzenie(BaseModel):
    stan: Literal['w_kolejce', 'w_toku', 'gotowe', 'blad']
    reklama_id: int | None = None
    blad: str | None = None


class NowyDowod(BaseModel):
    """Jedna wizyta sprawdzanego linku: zrzut ekranu jako PNG w base64 i HTML strony."""

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
