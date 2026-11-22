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
import patrol
import platnicy_domeny
import powiazane
import prog
import sprawdzenia
import wiek_domeny
from schematy import (
    Alert,
    Nagranie,
    Nauka,
    NowaReklama,
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
# 50 MB pliku w base64.
NAJWIEKSZE_NAGRANIE = 50 * 1024 * 1024 * 4 // 3 + 4

app = FastAPI(title='KLAKIER API',
              description='API systemu KLAKIER: zbiera reklamy inwestycyjne, ocenia ryzyko oszustwa i prowadzi sprawy analityka.')
app.add_api_websocket_route('/alerty', alerty.sluchaj)
app.include_router(historia.router)
app.include_router(prog.router)
app.include_router(powiazane.router)
app.include_router(domeny.router)
app.include_router(sprawdzenia.router)
app.include_router(patrol.router)
app.include_router(dowody.router)


@app.exception_handler(httpx.TransportError)
async def usluga_nie_odpowiada(zapytanie, blad):
    return JSONResponse({'detail': 'Usługa, która ocenia albo odczytuje reklamy, nie odpowiedziała.'}, status_code=503)


@app.get('/zdrowie', summary='Stan usługi', tags=['Usługa'])
def zdrowie():
    return {'ok': True}


@app.post('/reklamy', response_model=Reklama, status_code=201, summary='Dodaj reklamę', tags=['Reklamy'])
def dodaj_reklame(reklama: NowaReklama):
    # Sprawdzane przed oceną, żeby ponowne uruchomienie zbieracza nie kosztowało wywołań modelu.
    if baza.jest(reklama.zrodlo, reklama.id_zrodla):
        raise HTTPException(409, 'Ta reklama jest już w bazie')
    ocena = ocen(reklama.model_dump())
    wiersz = baza.dodaj(reklama.model_dump(), ocena)
    if wiersz is None:
        raise HTTPException(409, 'Ta reklama jest już w bazie')
    wiersz = z_sygnalem_domeny([wiersz])[0]
    zapisana = Reklama.model_validate(wiersz)
    if zapisana.poziom == 'wysokie':
        alerty.wyslij(Alert.model_validate(zapisana.model_dump()).model_dump_json())
    return wiersz


@app.get('/reklamy', response_model=list[Reklama], summary='Lista reklam', tags=['Reklamy'])
def lista_reklam(werdykt: Werdykt | None = None, status: Status | None = None, min_ryzyko: float = 0,
                 od: datetime | None = None):
    return z_sygnalem_domeny(baza.lista(werdykt, status, min_ryzyko, od))


@app.get('/reklamy/{id}', response_model=Reklama, summary='Jedna reklama', tags=['Reklamy'])
def jedna_reklama(id: int):
    return z_sygnalem_domeny([znaleziona(baza.jedna(id))])[0]


@app.patch('/reklamy/{id}', response_model=Reklama, summary='Zmień reklamę', tags=['Reklamy'])
def zmien_reklame(id: int, zmiana: ZmianaReklamy, kto: str = Header('analityk', alias='X-Analityk')):
    przed = znaleziona(baza.jedna(id))
    zmiany = zmiana.model_dump(exclude_unset=True)
    zmieniona = znaleziona(baza.zmien(id, zmiany))
    historia.zapisz(kto, opis_zmian.zmiany_analityka(przed, zmiany))
    return z_sygnalem_domeny([zmieniona])[0]


@app.get('/reklamy/{id}/podobne', response_model=list[PodobnaReklama], summary='Podobne reklamy', tags=['Reklamy'])
def podobne_reklamy(id: int):
    znaleziona(baza.jedna(id))
    try:
        return z_sygnalem_domeny(baza.podobne(id))
    except psycopg.errors.QueryCanceled as blad:
        raise HTTPException(503, 'Szukanie podobnych reklam trwało za długo.') from blad


@app.put('/reklamy/{id}/obraz', response_model=Reklama, summary='Dodaj obraz', tags=['Dla zbieraczy'])
def dodaj_obraz(id: int, obraz: Obraz):
    reklama = znaleziona(baza.jedna(id))
    typ, dane = odkoduj_obraz(obraz.obraz)
    if not reklama['tekst'].strip():
        tekst = odczytaj_tekst(obraz.obraz)
        ocena = ocen({**reklama, 'tekst': tekst})
        baza.zapisz_tekst(id, tekst)
        zapisz_ponowna_ocene(reklama, ocena, 'model')
    return z_sygnalem_domeny([baza.zapisz_obraz(id, typ, dane)])[0]


@app.put('/reklamy/{id}/nagranie', response_model=Reklama, summary='Dodaj nagranie', tags=['Reklamy'])
def dodaj_nagranie(id: int, nagranie: Nagranie, kto: str = Header('analityk', alias='X-Analityk')):
    reklama = znaleziona(baza.jedna(id))
    if len(nagranie.nagranie) > NAJWIEKSZE_NAGRANIE:
        raise HTTPException(422, 'Nagranie jest większe niż 50 MB.')
    mowa = posluchaj(nagranie.nagranie)
    ocena = ocen({**reklama, 'mowa': mowa})
    baza.zapisz_mowe(id, mowa)
    historia.zapisz(kto, [(id, f'Dodano nagranie: {len(mowa)} znaków mowy' if mowa else 'Dodano nagranie bez mowy')])
    zapisz_ponowna_ocene(reklama, ocena, kto)
    return z_sygnalem_domeny([baza.jedna(id)])[0]


@app.get('/reklamy/{id}/obraz', summary='Pobierz obraz', tags=['Reklamy'])
def pobierz_obraz(id: int):
    obraz = baza.obraz(id)
    if obraz is None:
        raise HTTPException(404, 'Ta reklama nie ma obrazu')
    return Response(obraz['dane'], media_type=obraz['typ'])


@app.put('/strony/{domena}', response_model=Strona, summary='Zapisz stronę', tags=['Dla zbieraczy'])
def zapisz_strone(domena: str, pomiar: PomiarStrony):
    return baza.zapisz_strone(domena, pomiar.model_dump())


@app.post('/ucz', response_model=Nauka, summary='Doucz model', tags=['Model i próg'])
def ucz(kto: str = Header('model', alias='X-Analityk')):
    przyklady = baza.przyklady_analityka()
    nauka = httpx.post(f'{AI_URL}/ucz', json={'przyklady': przyklady}, timeout=120).raise_for_status().json()
    przed = oceny_modelu()
    przeliczono = przelicz_wszystkie()
    historia.zapisz(kto, opis_zmian.zmiany_modelu(przed, oceny_modelu()))
    return {'przyklady': nauka['przyklady'], 'przeliczono': przeliczono}


@app.get('/rodzaje', response_model=list[str], summary='Lista rodzajów', tags=['Model i próg'])
def rodzaje():
    return httpx.get(f'{AI_URL}/rodzaje', timeout=10).raise_for_status().json()


@app.get('/progi', summary='Progi modelu', tags=['Model i próg'])
def progi():
    return httpx.get(f'{AI_URL}/progi', timeout=10).raise_for_status().json()


@app.post('/odczytaj', response_model=OdczytanyTekst, summary='Odczytaj tekst z obrazu', tags=['Model i próg'])
def odczytaj(obraz: Obraz):
    return {'tekst': odczytaj_tekst(obraz.obraz)}


def ocen(reklama, klient=httpx):
    dane = {pole: reklama[pole] for pole in ('tekst', 'reklamodawca', 'url', 'zrodlo')}
    dane['mowa'] = reklama.get('mowa')
    return klient.post(f'{AI_URL}/ocen', json=dane, timeout=60).raise_for_status().json()


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


def posluchaj(nagranie):
    """Mowa z nagrania w base64, odczytana przez usługę odczyt."""
    try:
        with ODCZYT_PO_KOLEI:
            odpowiedz = httpx.post(f'{ODCZYT_URL}/posluchaj', json={'nagranie': nagranie}, timeout=300)
    except httpx.TransportError as blad:
        raise HTTPException(503, 'Odczyt mowy jest niedostępny.') from blad
    if odpowiedz.status_code != 200:
        try:
            opis = odpowiedz.json()['detail']
        except (ValueError, KeyError) as blad:
            raise HTTPException(503, 'Odczyt mowy nie powiódł się.') from blad
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


def zapisz_ponowna_ocene(przed, ocena, kto):
    """przed: wiersz reklamy sprzed zmiany jej treści; z nim porównany jest werdykt i poziom po nowej ocenie."""
    baza.zapisz_oceny([{'id': przed['id'], **ocena}])
    stara, nowa = map(Reklama.model_validate, z_sygnalem_domeny([przed, baza.jedna(przed['id'])]))
    historia.zapisz(kto, opis_zmian.zmiany_modelu({stara.id: stara.model_dump(include={'werdykt', 'poziom'})},
                                                  {nowa.id: nowa.model_dump(include={'werdykt', 'poziom'})}))
    if nowa.poziom == 'wysokie' and stara.poziom != 'wysokie':
        alerty.wyslij(Alert.model_validate(nowa.model_dump()).model_dump_json())


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
