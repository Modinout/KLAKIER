# Moduł M3: wykrywa mowę o doradztwie inwestycyjnym lub zarządzaniu portfelem od płatnika spoza rejestrów KNF.
#   from doradztwo import sygnaly
#   sygnaly('Family office dla zamożnych rodzin.', {'stan': 'poza_listami', ...})
#   -> [{'modul': 'M3', 'kod': 'doradztwo_bez_zezwolenia', 'opis': '...', 'podstawa': '...'}]
import re

from wymogi import cytat, twierdzenie

PODSTAWA = 'art. 69 ust. 2 pkt 4 i 5 oraz art. 76 ustawy o obrocie instrumentami finansowymi'

PODSTAWA_REKOMENDACJI = (
    'art. 20 rozporządzenia MAR (UE 596/2014) o rekomendacjach inwestycyjnych; '
    'art. 76 ustawy o obrocie instrumentami finansowymi'
)

OFERTA = re.compile(
    r'\bdoradztw\w* inwestycyjn\w*|\bzarządzani\w+ (?:majątkiem|aktywami)'
    r'|\bfamily office|\bwealth management|\basset management'
)
# Sygnały rozsyłane całej grupie to rekomendacje ogólne: zezwolenia wymaga dopiero rada dla konkretnej osoby.
REKOMENDACJE = re.compile(
    r'\bsygnał\w* (?:inwestycyjn\w+|tradingow\w+|giełdow\w+|forex)|\brekomendacj\w+ (?:kupna|sprzedaży)'
)


ZACHETA = re.compile(
    r'\boferuj\w*|\bświadcz\w*|\bzapraszamy\b|\bdołącz\w*|\botrzym\w*|\bpobierz\b|\bpomagamy\b|\bpomagają\b|\bzapewniamy\b'
    r'|\bnow\w+ usług\w+|\bbieżące\b|\bprofesjonaln\w+|\bsubskryb\w*|\babonament\w*|\bwe offer\b|\bjoin\b'
)
# Prawnicy i doradcy podatkowi obsługują family office, nie zarządzając niczyimi pieniędzmi.
OBSLUGA_PRAWNA = re.compile(r'\bobsług\w+ prawn\w+|\bkancelari\w+|\bradc\w+ prawn\w+|\badwoka\w+|\blegal\b')
_OTOCZENIE = 100


def oferta(tekst, trafienie):
    """Prawda, gdy słowa wokół trafienia brzmią jak oferta, a nie jak menu strony."""
    wokol = tekst[max(0, trafienie.start() - _OTOCZENIE):trafienie.end() + _OTOCZENIE]
    slowa = [s for s in wokol.split() if s[0].isalpha()]
    # Menu to ciąg etykiet pisanych wielką literą, a zdanie jest głównie małymi.
    menu = sum(s[0].isupper() for s in slowa) > 0.4 * len(slowa) or 'menu' in wokol.casefold().split()
    return not menu and bool(ZACHETA.search(wokol.casefold())) and not OBSLUGA_PRAWNA.search(tekst.casefold())


def sygnaly(tekst, rejestr):
    """Jedno ustalenie, gdy oferta pochodzi od płatnika, którego nie zna żaden rejestr firm inwestycyjnych KNF."""
    # Płatnik, którego marka jest w rejestrach pod innym podmiotem, to ustalenie modułu M1.
    if not tekst or (rejestr and rejestr['stan'] != 'poza_listami'):
        return []
    trafienie = twierdzenie(OFERTA, tekst.casefold(), lambda t: oferta(tekst, t))
    if not trafienie:
        trafienie = twierdzenie(REKOMENDACJE, tekst.casefold(), lambda t: oferta(tekst, t))
        if not trafienie:
            return []
        opis = (f'Tekst zachęca do korzystania z sygnałów lub rekomendacji inwestycyjnych („{cytat(tekst, trafienie)}”). '
                'Kierowane do ogółu nie wymagają zezwolenia, ale muszą być rzetelne i ujawniać konflikt interesów; '
                'kierowane do konkretnej osoby są doradztwem inwestycyjnym.')
        return [{'modul': 'M3', 'kod': 'rekomendacje_ogolne', 'opis': opis, 'podstawa': PODSTAWA_REKOMENDACJI}]
    if rejestr:
        uprawnienia = 'Firmy, która to oferuje lub poleca, nie ma w rejestrach firm inwestycyjnych KNF.'
    else:
        uprawnienia = 'Nie wiadomo, kto stoi za tym tekstem, więc zezwolenia nie da się potwierdzić.'
    opis = f'Tekst mówi o doradztwie inwestycyjnym lub zarządzaniu portfelem („{cytat(tekst, trafienie)}”). {uprawnienia}'
    return [{'modul': 'M3', 'kod': 'doradztwo_bez_zezwolenia', 'opis': opis, 'podstawa': PODSTAWA}]
