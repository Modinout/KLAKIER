# Module M3: finds talk of investment advice or portfolio management from a payer outside the KNF lists.
#   from doradztwo import sygnaly
#   sygnaly('Family office dla zamożnych rodzin.', {'stan': 'poza_listami', ...})
#   -> [{'modul': 'M3', 'kod': 'doradztwo_bez_zezwolenia', 'opis': '...', 'podstawa': '...'}]
import re

from wymogi import cytat, twierdzenie

PODSTAWA = 'art. 69 ust. 2 pkt 4 i 5 oraz art. 76 ustawy o obrocie instrumentami finansowymi'

OFERTA = re.compile(
    r'\bdoradztw\w* inwestycyjn\w*|\bzarządzani\w+ (?:majątkiem|aktywami)'
    r'|\bfamily office|\bwealth management|\basset management'
    r'|\bsygnał\w* (?:inwestycyjn\w+|tradingow\w+|giełdow\w+|forex)|\brekomendacj\w+ (?:kupna|sprzedaży)'
)


def sygnaly(tekst, rejestr):
    """One finding when the offer comes from a payer that no KNF list of investment firms knows."""
    # A payer whose brand is on the lists under another entity is the finding of module M1.
    if not tekst or (rejestr and rejestr['stan'] != 'poza_listami'):
        return []
    trafienie = twierdzenie(OFERTA, tekst.casefold())
    if not trafienie:
        return []
    if rejestr:
        uprawnienia = 'Płatnika nie ma na listach firm inwestycyjnych KNF.'
    else:
        uprawnienia = 'Płatnik nie jest znany, więc zezwolenia nie da się potwierdzić.'
    opis = f'Tekst mówi o doradztwie inwestycyjnym lub zarządzaniu portfelem („{cytat(tekst, trafienie)}”). {uprawnienia}'
    return [{'modul': 'M3', 'kod': 'doradztwo_bez_zezwolenia', 'opis': opis, 'podstawa': PODSTAWA}]
