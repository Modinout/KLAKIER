# To, co przeglądarka zobaczyła przy każdej wizycie sprawdzanego linku: dodaje to robotnik, analitycy pobierają jako dowód.
import base64
import binascii
import hashlib
import io
import json
import zipfile

from fastapi import APIRouter, HTTPException, Response

import baza
from schematy import Dowod, NowyDowod

PNG = b'\x89PNG\r\n\x1a\n'

router = APIRouter()


@router.post('/reklamy/{id}/dowody', response_model=Dowod, status_code=201)
def dodaj_dowod(id: int, dowod: NowyDowod):
    """Robotnik dodaje tu wizytę; hasze liczone są z bajtów w takiej postaci, w jakiej zostały zapisane."""
    znaleziona(baza.jedna(id))
    try:
        obraz = base64.b64decode(dowod.obraz, validate=True)
    except binascii.Error as blad:
        raise HTTPException(422, 'To nie jest obraz PNG.') from blad
    if not obraz.startswith(PNG):
        raise HTTPException(422, 'To nie jest obraz PNG.')
    html = dowod.html.encode()
    return baza.dodaj_dowod(id, {**dowod.model_dump(), 'obraz': obraz, 'html': html,
                                 'sha256_obrazu': hashlib.sha256(obraz).hexdigest(),
                                 'sha256_html': hashlib.sha256(html).hexdigest()})


@router.get('/reklamy/{id}/dowody', response_model=list[Dowod])
def dowody(id: int):
    znaleziona(baza.jedna(id))
    return baza.dowody(id)


@router.get('/dowody/{id}/obraz')
def obraz_dowodu(id: int):
    return Response(znaleziony(baza.dowod(id))['obraz'], media_type='image/png')


@router.get('/dowody/{id}/html')
def html_dowodu(id: int):
    # Zapisana strona może zawierać skrypty, więc przeglądarka dostaje ją zawsze tylko jako plik tekstowy do zapisania.
    return Response(znaleziony(baza.dowod(id))['html'], media_type='text/plain; charset=utf-8',
                    headers={'Content-Disposition': f'attachment; filename="dowod-{id}.html"',
                             'X-Content-Type-Options': 'nosniff'})


@router.get('/reklamy/{id}/paczka')
def paczka(id: int):
    """ZIP z plikami każdej wizyty i manifestem ich SHA-256 policzonych w chwili, gdy wizyta wpłynęła."""
    reklama = znaleziona(baza.jedna(id))
    bufor = io.BytesIO()
    with zipfile.ZipFile(bufor, 'w', zipfile.ZIP_DEFLATED) as archiwum:
        wizyty = []
        for dowod in baza.dowody_z_plikami(id):
            pliki = []
            for rozszerzenie, dane, skrot in (('png', dowod['obraz'], dowod['sha256_obrazu']),
                                              ('html', dowod['html'], dowod['sha256_html'])):
                nazwa = f'{dowod["id"]}-{dowod["rodzaj"]}.{rozszerzenie}'
                archiwum.writestr(nazwa, dane)
                pliki.append({'plik': nazwa, 'sha256': skrot})
            wizyty.append({'id': dowod['id'], 'kiedy': dowod['kiedy'].isoformat(), 'rodzaj': dowod['rodzaj'],
                           'adres': dowod['adres'], 'lancuch': dowod['lancuch'], 'pliki': pliki})
        manifest = {'reklama_id': id, 'url': reklama['url'], 'dowody': wizyty}
        archiwum.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2))
    return Response(bufor.getvalue(), media_type='application/zip',
                    headers={'Content-Disposition': f'attachment; filename="reklama-{id}-dowody.zip"'})


def znaleziona(reklama):
    if reklama is None:
        raise HTTPException(404, 'Nie ma takiej reklamy')
    return reklama


def znaleziony(dowod):
    if dowod is None:
        raise HTTPException(404, 'Nie ma takiego dowodu')
    return dowod
