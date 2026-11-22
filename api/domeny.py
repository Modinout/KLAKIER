from fastapi import APIRouter

import baza
from schematy import Domena, RejestracjaDomeny

router = APIRouter()


@router.put('/domeny/{domena}', response_model=Domena)
def zapisz_rejestracje(domena: str, rejestracja: RejestracjaDomeny):
    """Zastępuje wcześniejszą datę domeny."""
    with baza.polacz() as polaczenie:
        return polaczenie.execute(
            """
            INSERT INTO domeny (domena, zarejestrowano, sprawdzono) VALUES (%s, %s, now())
            ON CONFLICT (domena) DO UPDATE SET zarejestrowano = EXCLUDED.zarejestrowano, sprawdzono = EXCLUDED.sprawdzono
            RETURNING *
            """,
            [domena, rejestracja.zarejestrowano],
        ).fetchone()


def daty():
    """Daty rejestracji według domeny."""
    with baza.polacz() as polaczenie:
        return {wiersz['domena']: wiersz['zarejestrowano']
                for wiersz in polaczenie.execute('SELECT domena, zarejestrowano FROM domeny').fetchall()}
