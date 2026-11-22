# Domena docelowa zarejestrowana tuż przed emisją reklamy inwestycyjnej: strony-oszustwa zakłada się na jedną
# kampanię i porzuca.
from datetime import date

from temat import o_inwestycjach

MLODA_DNI = 30


def sygnaly(reklama, zarejestrowano):
    """Ustalenia dla reklamy; zarejestrowano to data rejestracji jej domeny docelowej według RDAP albo None."""
    if zarejestrowano is None or not o_inwestycjach(reklama['tekst'] + ' ' + (reklama['reklamodawca'] or '')):
        return []
    # Domena zarejestrowana po emisji reklamy została zarejestrowana ponownie później,
    # więc jej data nic o reklamie nie mówi.
    dzien_reklamy = reklama['opublikowano'] or date.today()
    if not 0 <= (dzien_reklamy - zarejestrowano).days < MLODA_DNI:
        return []
    kiedy = 'publikacją reklamy' if reklama['opublikowano'] else 'dniem dzisiejszym'
    return [{'modul': 'M1', 'kod': 'mloda_domena',
             'opis': f'Domenę {reklama["domena"]} zarejestrowano {zarejestrowano:%d.%m.%Y}, mniej niż {MLODA_DNI} dni '
                     f'przed {kiedy}.',
             'podstawa': 'Data rejestracji domeny według RDAP (rdap.org)'}]
