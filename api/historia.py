from urllib.parse import unquote

from fastapi import APIRouter, HTTPException

import baza
from schematy import WpisHistorii

router = APIRouter()


@router.get('/reklamy/{id}/historia', response_model=list[WpisHistorii])
def historia_reklamy(id: int):
    if baza.jedna(id) is None:
        raise HTTPException(404, 'Nie ma takiej reklamy')
    with baza.polacz() as polaczenie:
        return polaczenie.execute(
            'SELECT kiedy, kto, co FROM historia WHERE reklama_id = %s ORDER BY kiedy DESC, id DESC', [id]
        ).fetchall()


def zapisz(kto, wpisy):
    """wpisy: (reklama_id, co) pairs; kto: the X-Analityk header, or the name used when it is missing."""
    # The panel percent-encodes the name, since a header carries only Latin-1 and so no ł or ś.
    with baza.polacz() as polaczenie:
        polaczenie.cursor().executemany(
            'INSERT INTO historia (reklama_id, kto, co) VALUES (%s, %s, %s)',
            [(reklama_id, unquote(kto), co) for reklama_id, co in wpisy],
        )
