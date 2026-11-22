from fastapi import APIRouter, HTTPException

import baza
from kontakty import kontakty
from schematy import PowiazanaReklama
from tytul import tytul

router = APIRouter()


@router.get('/reklamy/{id}/powiazane', response_model=list[PowiazanaReklama], summary='Powiązane reklamy',
            tags=['Reklamy'])
def powiazane_reklamy(id: int):
    reklama = baza.jedna(id)
    if reklama is None:
        raise HTTPException(404, 'Nie ma takiej reklamy')
    szukane = kontakty(reklama['tekst'])
    if not szukane:
        return []
    with baza.polacz() as polaczenie:
        inne = polaczenie.execute(
            """
            SELECT id, reklamodawca, domena, url, tekst, sygnaly, sygnaly_zbieracza FROM reklamy
            WHERE id <> %s ORDER BY id
            """,
            [id],
        ).fetchall()
    powiazane = []
    for inna in inne:
        wspolne = szukane & kontakty(inna['tekst'])
        if wspolne:
            powod, wartosc = min(wspolne)
            powiazane.append({'id': inna['id'], 'tytul': tytul(inna), 'powod': powod, 'wartosc': wartosc})
    return powiazane
