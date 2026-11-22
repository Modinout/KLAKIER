import base64
import binascii
import os
import threading
from datetime import datetime

import httpx
import psycopg
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse

import alerty
import baza
import ostrzezenie_strony
import platnicy_domeny
from schematy import (
    Alert,
    DodanyRodzaj,
    Nauka,
    NowaReklama,
    NowyRodzaj,
    Obraz,
    OdczytanyTekst,
    PodobnaReklama,
    PomiarStrony,
    Reklama,
    Status,
    Strona,
    Werdykt,
    ZmianaReklamy,
)

AI_URL = os.environ['AI_URL']
ODCZYT_URL = os.environ['ODCZYT_URL']
# The odczyt service reads one picture at a time and takes up to minutes per picture.
ODCZYT_PO_KOLEI = threading.Lock()

app = FastAPI(title='KLAKIER API')
app.add_api_websocket_route('/alerty', alerty.sluchaj)


@app.exception_handler(httpx.TransportError)
async def usluga_nie_odpowiada(zapytanie, blad):
    return JSONResponse({'detail': 'Usługa, która ocenia albo odczytuje reklamy, nie odpowiedziała.'}, status_code=503)


@app.get('/zdrowie')
def zdrowie():
    return {'ok': True}


@app.post('/reklamy', response_model=Reklama, status_code=201)
def dodaj_reklame(reklama: NowaReklama):
    # Checked before scoring so a re-run of the collector costs no model calls.
    if baza.jest(reklama.zrodlo, reklama.id_zrodla):
        raise HTTPException(409, 'Ta reklama jest już w bazie')
    ocena = ocen(reklama.model_dump())
    sedzia = None if ocena['pewny'] else drugi_sedzia(reklama.tekst)
    wiersz = baza.dodaj(reklama.model_dump(), ocena, sedzia)
    if wiersz is None:
        raise HTTPException(409, 'Ta reklama jest już w bazie')
    wiersz = z_sygnalem_domeny([wiersz])[0]
    zapisana = Reklama.model_validate(wiersz)
    if zapisana.poziom == 'wysokie':
        alerty.wyslij(Alert.model_validate(zapisana.model_dump()).model_dump_json())
    return wiersz


@app.get('/reklamy', response_model=list[Reklama])
def lista_reklam(werdykt: Werdykt | None = None, status: Status | None = None, min_ryzyko: float = 0,
                 od: datetime | None = None):
    return z_sygnalem_domeny(baza.lista(werdykt, status, min_ryzyko, od))


@app.get('/reklamy/{id}', response_model=Reklama)
def jedna_reklama(id: int):
    return z_sygnalem_domeny([znaleziona(baza.jedna(id))])[0]


@app.patch('/reklamy/{id}', response_model=Reklama)
def zmien_reklame(id: int, zmiana: ZmianaReklamy):
    return z_sygnalem_domeny([znaleziona(baza.zmien(id, zmiana.model_dump(exclude_unset=True)))])[0]


@app.get('/reklamy/{id}/podobne', response_model=list[PodobnaReklama])
def podobne_reklamy(id: int):
    znaleziona(baza.jedna(id))
    try:
        return z_sygnalem_domeny(baza.podobne(id))
    except psycopg.errors.QueryCanceled as blad:
        raise HTTPException(503, 'Szukanie podobnych reklam trwało za długo.') from blad


@app.put('/reklamy/{id}/obraz', response_model=Reklama)
def dodaj_obraz(id: int, obraz: Obraz):
    reklama = znaleziona(baza.jedna(id))
    typ, dane = odkoduj_obraz(obraz.obraz)
    if not reklama['tekst'].strip():
        tekst = odczytaj_tekst(obraz.obraz)
        ocena = ocen({**reklama, 'tekst': tekst})
        baza.zapisz_tekst(id, tekst)
        baza.zapisz_oceny([{'id': id, **ocena}])
    return z_sygnalem_domeny([baza.zapisz_obraz(id, typ, dane)])[0]


@app.get('/reklamy/{id}/obraz')
def pobierz_obraz(id: int):
    obraz = baza.obraz(id)
    if obraz is None:
        raise HTTPException(404, 'Ta reklama nie ma obrazu')
    return Response(obraz['dane'], media_type=obraz['typ'])


@app.put('/strony/{domena}', response_model=Strona)
def zapisz_strone(domena: str, pomiar: PomiarStrony):
    return baza.zapisz_strone(domena, pomiar.model_dump())


@app.post('/ucz', response_model=Nauka)
def ucz():
    przyklady = baza.przyklady_analityka()
    nauka = httpx.post(f'{AI_URL}/ucz', json={'przyklady': przyklady}, timeout=120).raise_for_status().json()
    return {'przyklady': nauka['przyklady'], 'przeliczono': przelicz_wszystkie()}


@app.get('/rodzaje', response_model=list[str])
def rodzaje():
    return httpx.get(f'{AI_URL}/rodzaje', timeout=10).raise_for_status().json()


@app.post('/rodzaje', response_model=DodanyRodzaj)
def dodaj_rodzaj(rodzaj: NowyRodzaj):
    odpowiedz = httpx.post(f'{AI_URL}/rodzaje', json=rodzaj.model_dump(), timeout=300)
    if odpowiedz.status_code in (409, 503):
        raise HTTPException(odpowiedz.status_code, odpowiedz.json()['detail'])
    dodany = odpowiedz.raise_for_status().json()
    return {**dodany, 'przeliczono': przelicz_wszystkie()}


@app.get('/progi')
def progi():
    return httpx.get(f'{AI_URL}/progi', timeout=10).raise_for_status().json()


@app.post('/odczytaj', response_model=OdczytanyTekst)
def odczytaj(obraz: Obraz):
    return {'tekst': odczytaj_tekst(obraz.obraz)}


def ocen(reklama, klient=httpx):
    dane = {pole: reklama[pole] for pole in ('tekst', 'reklamodawca', 'url', 'zrodlo')}
    return klient.post(f'{AI_URL}/ocen', json=dane, timeout=60).raise_for_status().json()


def drugi_sedzia(tekst):
    """Verdict of the big model, or None when it is not configured or did not answer."""
    odpowiedz = httpx.post(f'{AI_URL}/drugi_sedzia', json={'tekst': tekst}, timeout=120)
    if odpowiedz.status_code == 503:
        return None
    return odpowiedz.raise_for_status().json()


def odczytaj_tekst(obraz):
    """Text of a base64 picture, read by the odczyt service."""
    try:
        with ODCZYT_PO_KOLEI:
            odpowiedz = httpx.post(f'{ODCZYT_URL}/odczytaj', json={'obraz': obraz}, timeout=300)
    except httpx.TransportError as blad:
        raise HTTPException(503, 'Odczyt obrazów jest niedostępny.') from blad
    if odpowiedz.status_code != 200:
        raise HTTPException(odpowiedz.status_code, odpowiedz.json()['detail'])
    return odpowiedz.json()['tekst']


def odkoduj_obraz(obraz):
    """Content type and bytes of a base64 PNG or JPEG, told apart by the first bytes of the file."""
    try:
        dane = base64.b64decode(obraz, validate=True)
    except binascii.Error as blad:
        raise HTTPException(422, 'To nie jest obraz PNG ani JPEG.') from blad
    if dane.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png', dane
    if dane.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg', dane
    raise HTTPException(422, 'To nie jest obraz PNG ani JPEG.')


def przelicz_wszystkie():
    """Scores every stored ad again with the current model and returns how many there were."""
    reklamy = baza.do_oceny()
    # One client for the whole run: opening a new one per ad takes longer than scoring the ad.
    with httpx.Client() as klient:
        baza.zapisz_oceny([{'id': reklama['id'], **ocen(reklama, klient)} for reklama in reklamy])
    return len(reklamy)


def z_sygnalem_domeny(wiersze):
    """Rows of the reklamy table with the findings about their landing domain: payers compared with the domain, and
    the risk warning on its page.

    Computed on each read, not stored: a re-score rewrites the stored signals, and a new ad or a new measurement of
    the page must show on the older ads of the domain at once.
    """
    sygnaly = platnicy_domeny.sygnaly_domen(baza.platnicy_domen())
    strony = baza.strony()
    return [{**wiersz, 'sygnaly': wiersz['sygnaly'] + platnicy_domeny.sygnaly_reklamy(wiersz, sygnaly)
             + ostrzezenie_strony.sygnaly(wiersz['domena'], strony.get(wiersz['domena']))}
            for wiersz in wiersze]


def znaleziona(wiersz):
    if wiersz is None:
        raise HTTPException(404, 'Nie ma takiej reklamy')
    return wiersz
