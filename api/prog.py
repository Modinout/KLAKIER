from fastapi import APIRouter

import baza
from schematy import Prog

router = APIRouter()


@router.get('/prog', response_model=Prog, summary='Czytaj próg', tags=['Model i próg'])
def czytaj_prog():
    return {'prog': zapisany()}


@router.put('/prog', response_model=Prog, summary='Zmień próg', tags=['Model i próg'])
def zmien_prog(prog: Prog):
    with baza.polacz() as polaczenie:
        polaczenie.execute('UPDATE ustawienia SET prog = %s', [prog.prog])
    return prog


def zapisany():
    with baza.polacz() as polaczenie:
        return polaczenie.execute('SELECT prog FROM ustawienia').fetchone()['prog']


def ponad_progiem(reklama, prog):
    """Czy sam model tekstowy czyni reklamę wysoką: jego ryzyko jest równe progowi lub go przekracza."""
    # Model daje ryzyko także reklamie bez tekstu i bez mowy, ale bez werdyktu.
    return bool(reklama['tekst'].strip() or (reklama['mowa'] or '').strip()) and reklama['ryzyko'] >= prog
