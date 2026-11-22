from urllib.parse import unquote

from fastapi import APIRouter, HTTPException

import baza
from schematy import WpisHistorii

router = APIRouter()


@router.get('/reklamy/{id}/historia', response_model=list[WpisHistorii], summary='Historia reklamy', tags=['Reklamy'])
def historia_reklamy(id: int):
    if baza.jedna(id) is None:
        raise HTTPException(404, 'Nie ma takiej reklamy')
    with baza.polacz() as polaczenie:
        return polaczenie.execute(
            'SELECT kiedy, kto, co FROM historia WHERE reklama_id = %s ORDER BY kiedy DESC, id DESC', [id]
        ).fetchall()


def zapisz(kto, wpisy):
    """wpisy: pary (reklama_id, co); kto: nagłówek X-Analityk albo nazwa używana, gdy go brak."""
    # Panel koduje nazwę procentowo, bo nagłówek niesie tylko Latin-1, a więc bez ł i ś.
    with baza.polacz() as polaczenie:
        polaczenie.cursor().executemany(
            'INSERT INTO historia (reklama_id, kto, co) VALUES (%s, %s, %s)',
            [(reklama_id, unquote(kto), co) for reklama_id, co in wpisy],
        )
