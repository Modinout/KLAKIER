# A landing domain registered just before an investment ad ran: scam sites are set up for one campaign and dropped.
from datetime import date

from temat import o_inwestycjach

MLODA_DNI = 30


def sygnaly(reklama, zarejestrowano):
    """Findings for an ad; zarejestrowano is the registration date of its landing domain by RDAP, or None."""
    if zarejestrowano is None or not o_inwestycjach(reklama['tekst'] + ' ' + (reklama['reklamodawca'] or '')):
        return []
    # A domain registered after the ad ran was registered again later, so its date says nothing about the ad.
    dzien_reklamy = reklama['opublikowano'] or date.today()
    if not 0 <= (dzien_reklamy - zarejestrowano).days < MLODA_DNI:
        return []
    kiedy = 'publikacją reklamy' if reklama['opublikowano'] else 'dniem dzisiejszym'
    return [{'modul': 'M1', 'kod': 'mloda_domena',
             'opis': f'Domenę {reklama["domena"]} zarejestrowano {zarejestrowano:%d.%m.%Y}, mniej niż {MLODA_DNI} dni '
                     f'przed {kiedy}.',
             'podstawa': 'Data rejestracji domeny według RDAP (rdap.org)'}]
