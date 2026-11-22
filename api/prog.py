from fastapi import APIRouter

import baza
from schematy import Prog

router = APIRouter()


@router.get('/prog', response_model=Prog)
def czytaj_prog():
    return {'prog': zapisany()}


@router.put('/prog', response_model=Prog)
def zmien_prog(prog: Prog):
    with baza.polacz() as polaczenie:
        polaczenie.execute('UPDATE ustawienia SET prog = %s', [prog.prog])
    return prog


def zapisany():
    with baza.polacz() as polaczenie:
        return polaczenie.execute('SELECT prog FROM ustawienia').fetchone()['prog']


def ponad_progiem(reklama, prog):
    """Whether the text model alone makes the ad high level: its risk is at the threshold or over it."""
    # The model gives an ad without text a risk too, but no verdict.
    return bool(reklama['tekst'].strip()) and reklama['ryzyko'] >= prog
