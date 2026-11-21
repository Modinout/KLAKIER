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


ZACHETA = re.compile(
    r'\boferuj\w*|\bświadcz\w*|\bzapraszamy\b|\bdołącz\w*|\botrzym\w*|\bpobierz\b|\bpomagamy\b|\bpomagają\b|\bzapewniamy\b'
    r'|\bnow\w+ usług\w+|\bbieżące\b|\bprofesjonaln\w+|\bsubskryb\w*|\babonament\w*|\bwe offer\b|\bjoin\b'
)
# Lawyers and tax advisers serve family offices without managing anyone's money.
OBSLUGA_PRAWNA = re.compile(r'\bobsług\w+ prawn\w+|\bkancelari\w+|\bradc\w+ prawn\w+|\badwoka\w+|\blegal\b')
_OTOCZENIE = 100


def oferta(tekst, trafienie):
    """True when the words around the match read as an offer, not as a site menu."""
    wokol = tekst[max(0, trafienie.start() - _OTOCZENIE):trafienie.end() + _OTOCZENIE]
    slowa = [s for s in wokol.split() if s[0].isalpha()]
    # A menu is a run of capitalised labels; a sentence is mostly lower case.
    menu = sum(s[0].isupper() for s in slowa) > 0.4 * len(slowa)
    return not menu and bool(ZACHETA.search(wokol.casefold())) and not OBSLUGA_PRAWNA.search(tekst.casefold())


def sygnaly(tekst, rejestr):
    """One finding when the offer comes from a payer that no KNF list of investment firms knows."""
    # A payer whose brand is on the lists under another entity is the finding of module M1.
    if not tekst or (rejestr and rejestr['stan'] != 'poza_listami'):
        return []
    trafienie = twierdzenie(OFERTA, tekst.casefold(), lambda t: oferta(tekst, t))
    if not trafienie:
        return []
    if rejestr:
        uprawnienia = 'Firmy, która to oferuje, nie ma na listach firm inwestycyjnych KNF.'
    else:
        uprawnienia = 'Nie wiadomo, kto stoi za tym tekstem, więc zezwolenia nie da się potwierdzić.'
    opis = f'Tekst mówi o doradztwie inwestycyjnym lub zarządzaniu portfelem („{cytat(tekst, trafienie)}”). {uprawnienia}'
    return [{'modul': 'M3', 'kod': 'doradztwo_bez_zezwolenia', 'opis': opis, 'podstawa': PODSTAWA}]
