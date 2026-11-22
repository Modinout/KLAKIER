import base64
import binascii
import os
import threading
from datetime import datetime

import httpx
import psycopg
from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.responses import JSONResponse

import alerty
import baza
import domeny
import dowody
import historia
import opis_zmian
import ostrzezenie_strony
import platnicy_domeny
import powiazane
import prog
import sprawdzenia
import wiek_domeny
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
# Usługa odczyt czyta jeden obraz naraz i potrafi zająć nawet minuty na obraz.
ODCZYT_PO_KOLEI = threading.Lock()

app = FastAPI(title='KLAKIER API')
app.add_api_websocket_route('/alerty', alerty.sluchaj)
app.include_router(historia.router)
app.include_router(prog.router)
app.include_router(powiazane.router)
app.include_router(domeny.router)
app.include_router(sprawdzenia.router)
app.include_router(dowody.router)


@app.exception_handler(httpx.TransportError)
async def usluga_nie_odpowiada(zapytanie, blad):
    return JSONResponse({'detail': 'Usługa, która ocenia albo odczytuje reklamy, nie odpowiedziała.'}, status_code=503)


@app.get('/zdrowie')
def zdrowie():
    return {'ok': True}


@app.post('/reklamy', response_model=Reklama, status_code=201)
def dodaj_reklame(reklama: NowaReklama):
    # Sprawdzane przed oceną, żeby ponowne uruchomienie zbieracza nie kosztowało wywołań modelu.
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
def zmien_reklame(id: int, zmiana: ZmianaReklamy, kto: str = Header('analityk', alias='X-Analityk')):
    przed = znaleziona(baza.jedna(id))
    zmiany = zmiana.model_dump(exclude_unset=True)
    zmieniona = znaleziona(baza.zmien(id, zmiany))
    historia.zapisz(kto, opis_zmian.zmiany_analityka(przed, zmiany))
    return z_sygnalem_domeny([zmieniona])[0]


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
def ucz(kto: str = Header('model', alias='X-Analityk')):
    przyklady = baza.przyklady_analityka()
    nauka = httpx.post(f'{AI_URL}/ucz', json={'przyklady': przyklady}, timeout=120).raise_for_status().json()
    przed = oceny_modelu()
    przeliczono = przelicz_wszystkie()
    historia.zapisz(kto, opis_zmian.zmiany_modelu(przed, oceny_modelu()))
    return {'przyklady': nauka['przyklady'], 'przeliczono': przeliczono}


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
    """Werdykt dużego modelu albo None, gdy nie jest skonfigurowany lub nie odpowiedział."""
    odpowiedz = httpx.post(f'{AI_URL}/drugi_sedzia', json={'tekst': tekst}, timeout=120)
    if odpowiedz.status_code == 503:
        return None
    return odpowiedz.raise_for_status().json()


def odczytaj_tekst(obraz):
    """Tekst obrazu w base64, odczytany przez usługę odczyt."""
    try:
        with ODCZYT_PO_KOLEI:
            odpowiedz = httpx.post(f'{ODCZYT_URL}/odczytaj', json={'obraz': obraz}, timeout=300)
    except httpx.TransportError as blad:
        raise HTTPException(503, 'Odczyt obrazów jest niedostępny.') from blad
    if odpowiedz.status_code != 200:
        try:
            opis = odpowiedz.json()['detail']
        except (ValueError, KeyError) as blad:
            raise HTTPException(503, 'Odczyt obrazu nie powiódł się.') from blad
        raise HTTPException(odpowiedz.status_code, opis)
    return odpowiedz.json()['tekst']


def odkoduj_obraz(obraz):
    """Typ zawartości i bajty obrazu PNG lub JPEG w base64, rozpoznane po pierwszych bajtach pliku."""
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
    """Ocenia ponownie każdą zapisaną reklamę obecnym modelem i zwraca, ile ich było."""
    reklamy = baza.do_oceny()
    # Jeden klient na cały przebieg: otwieranie nowego dla każdej reklamy trwa dłużej niż jej ocena.
    with httpx.Client() as klient:
        baza.zapisz_oceny([{'id': reklama['id'], **ocen(reklama, klient)} for reklama in reklamy])
    return len(reklamy)


def oceny_modelu():
    """Werdykt modelu i poziom ryzyka każdej reklamy według id, tak jak pokazuje je panel."""
    reklamy = map(Reklama.model_validate, z_sygnalem_domeny(baza.lista(None, None, 0, None)))
    return {reklama.id: reklama.model_dump(include={'werdykt', 'poziom'}) for reklama in reklamy}


def z_sygnalem_domeny(wiersze):
    """Wiersze tabeli reklamy z ustaleniami o ich domenie docelowej: płatnicy porównani z domeną, ostrzeżenie o ryzyku
    na jej stronie i jej wiek; oraz z informacją, czy ryzyko modelu tekstowego sięga progu z GET /prog.

    Liczone przy każdym odczycie, nie zapisywane: ponowna ocena nadpisuje zapisane sygnały, a nowa reklama, nowy pomiar
    strony, nowa data domeny lub nowy próg muszą od razu pokazać się na starszych reklamach.
    """
    sygnaly = platnicy_domeny.sygnaly_domen(baza.platnicy_domen())
    strony = baza.strony()
    daty_domen = domeny.daty()
    prog_modelu = prog.zapisany()
    return [{**wiersz, 'sygnaly': wiersz['sygnaly'] + platnicy_domeny.sygnaly_reklamy(wiersz, sygnaly)
             + ostrzezenie_strony.sygnaly(wiersz['domena'], strony.get(wiersz['domena']))
             + wiek_domeny.sygnaly(wiersz, daty_domen.get(wiersz['domena'])),
             'ponad_progiem': prog.ponad_progiem(wiersz, prog_modelu)}
            for wiersz in wiersze]


def znaleziona(wiersz):
    if wiersz is None:
        raise HTTPException(404, 'Nie ma takiej reklamy')
    return wiersz
