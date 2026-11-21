# Checks the payer of an ad against the four KNF lists of investment firms in rejestr_knf.csv.
#   from rejestr import sprawdz
#   sprawdz('Tickmill Ltd')
#   -> {'stan': 'spoza_rejestru', 'podmiot': 'Tickmill Europe Ltd | Vipro Markets Ltd', 'panstwo': 'Cypr', 'lista': 'notyfikowane_zagraniczne'}
import csv
import pathlib
import re

STAN_NA = '21.11.2026'

FORMY_PRAWNE = [
    'spółka akcyjna', 'spolka akcyjna', 'spółka z ograniczoną odpowiedzialnością', 'sp z oo', 'spz oo', 'sp k',
    'sa', 's a', 'sau', 'ltd', 'limited', 'llc', 'inc', 'corp', 'co', 'gmbh', 'ag', 'kg', 'uab', 'as', 'a s',
    'bv', 'nv', 'plc', 'pty', 'pte', 'sro', 's r o', 'kft', 'doo', 'ead', 'ad', 'sas', 'sarl', 'srl', 'spa',
    'sl', 'lda', 'dac', 'se', 'oy', 'ab', 'asa', 'aps', 'cif', 'ocp',
]

# Words that tell apart entities of one brand (eToro Group vs Etoro Europe), not brands.
OGOLNE = {
    'europe', 'european', 'eu', 'global', 'group', 'international', 'int', 'markets', 'market', 'financial', 'finance',
    'services', 'service', 'securities', 'holdings', 'holding', 'operations', 'technology', 'technologies',
    'polska', 'poland', 'pl', 'cyprus', 'cy', 'malta', 'mt', 'ireland', 'ie', 'germany', 'deutschland', 'de',
    'netherlands', 'nl', 'france', 'fr', 'luxembourg', 'lu', 'spain', 'españa', 'es', 'italy', 'austria', 'at',
    'gibraltar', 'gi', 'estonia', 'ee', 'latvia', 'lv', 'lithuania', 'lt', 'bulgaria', 'bg', 'czech', 'cz',
    'slovakia', 'sk', 'liechtenstein', 'denmark', 'dk', 'sweden', 'uk', 'gb', 'us', 'usa', 'au', 'australia',
    'sg', 'singapore', 'hk', 'canada', 'ca', 'seychelles', 'sc', 'bvi', 'ae', 'za',
}

# Words too common to point at one firm: a name made only of them names no brand.
POSPOLITE = {
    'trade', 'trading', 'trader', 'capital', 'invest', 'investment', 'investments', 'prime', 'first', 'alpha',
    'asset', 'assets', 'wealth', 'management', 'partners', 'fx', 'forex', 'bank', 'broker', 'brokers', 'direct',
    'smart', 'best', 'top', 'one', 'money', 'crypto', 'digital', 'union', 'royal', 'swiss',
    'dom', 'maklerski', 'biuro', 'maklerskie', 'departament', 'banku', 'banking', 'inwestycyjny',
}

_FORMA = re.compile(r'\b(?:' + '|'.join(sorted(map(re.escape, FORMY_PRAWNE), key=len, reverse=True)) + r')\b')
_NAWIAS = re.compile(r'\(([^)]*)\)')


def slowa(nazwa):
    # Dots go without a space so that S.A. and SA read the same.
    tekst = re.sub(r'[\W_]+', ' ', nazwa.casefold().replace('.', ''))
    return ' '.join(tekst.split())


def normalizuj(nazwa):
    return ' '.join(_FORMA.sub(' ', slowa(nazwa)).split())


def klucz(nazwa):
    """Name for comparison. One made only of common words keeps its legal form: DOM MAKLERSKI INC S.A."""
    n = normalizuj(nazwa)
    if n and set(n.split()) <= POSPOLITE | OGOLNE:
        return slowa(nazwa)
    return n


def nazwy(wpis):
    """All names of a register entry: KNF joins alternatives with ' | ' and puts another full name in brackets."""
    wszystkie = []
    for czesc in wpis.split(' | '):
        inne = [n for n in _NAWIAS.findall(czesc) if normalizuj(n) != slowa(n)]
        if inne:
            wszystkie += inne + [_NAWIAS.sub(' ', czesc)]
        else:
            wszystkie.append(czesc)
    return [klucz(n) for n in wszystkie]


def rdzen(nazwa):
    return [s for s in nazwa.split() if s not in OGOLNE]


def wspolne(a, b):
    """How many brand words two name cores share, 0 when they are different brands."""
    if not a or not b:
        return 0
    krotszy, dluzszy = sorted([a, b], key=lambda r: (len(r), len(r[0])))
    if dluzszy[:len(krotszy)] == krotszy:
        return 0 if set(krotszy) <= POSPOLITE else len(krotszy)
    # A one-word brand with a country glued on: plus500 and plus500cy, but not revolut and revolution.
    marka = krotszy[0]
    doklejone = dluzszy[0][len(marka):]
    if len(krotszy) == 1 and len(marka) >= 5 and marka not in POSPOLITE and dluzszy[0].startswith(marka) and doklejone in OGOLNE:
        return 1
    return 0


def wynik(stan, wpis=None):
    wpis = wpis or {}
    return {'stan': stan, 'podmiot': wpis.get('nazwa'), 'panstwo': wpis.get('panstwo'), 'lista': wpis.get('lista')}


with pathlib.Path(__file__).with_name('rejestr_knf.csv').open(encoding='utf-8', newline='') as _plik:
    _NAZWY = [(wpis, nazwa) for wpis in csv.DictReader(_plik, delimiter=';') for nazwa in nazwy(wpis['nazwa']) if nazwa]
# Reversed so that a name listed twice points at its first entry.
_PO_NAZWIE = {nazwa: wpis for wpis, nazwa in reversed(_NAZWY)}

# Brands and short names of listed entities. A name misspelled against the register fails here, at import.
with pathlib.Path(__file__).with_name('marki_knf.csv').open(encoding='utf-8', newline='') as _plik:
    _MARKI = {klucz(r['marka']): _PO_NAZWIE[klucz(r['nazwa_w_rejestrze'])] for r in csv.DictReader(_plik, delimiter=';')}


def sprawdz(reklamodawca):
    nazwa = klucz(reklamodawca or '')
    if not nazwa:
        return None
    wpis = _PO_NAZWIE.get(nazwa) or _MARKI.get(nazwa)
    if wpis:
        return wynik('w_rejestrze', wpis)
    # There is no TFI list among the four, so a fund company cannot be checked here.
    if 'tfi' in nazwa.split() or 'towarzystwo funduszy inwestycyjnych' in nazwa:
        return wynik('tfi')
    najlepszy, ile = None, 0
    for wpis, n in _NAZWY:
        w = wspolne(rdzen(nazwa), rdzen(n))
        if w > ile:
            najlepszy, ile = wpis, w
    if najlepszy:
        return wynik('spoza_rejestru', najlepszy)
    # The four lists hold investment firms and bank brokerages. A bank without a brokerage is supervised
    # under another register, so it cannot be checked here.
    if 'bank' in nazwa.split():
        return wynik('bank')
    return wynik('poza_listami')


# For these sources the name is the author of the material, not the payer of an ad: the register gives no finding.
AUTOR_ZAMIAST_PLATNIKA = ('youtube', 'strony_doradcow')


def sygnaly(platnik, rejestr, zrodlo=None):
    """Findings for the analyst: one signal when the payer is not on the lists, none otherwise."""
    if zrodlo in AUTOR_ZAMIAST_PLATNIKA:
        return []
    podstawa = f'Listy KNF, stan na {STAN_NA}'
    if rejestr and rejestr['stan'] == 'spoza_rejestru':
        opis = f'Płatnik „{platnik}” nie figuruje w rejestrach KNF. Marka odpowiada wpisowi „{rejestr["podmiot"]}” ({rejestr["panstwo"]}).'
        return [{'modul': 'M1', 'kod': 'platnik_spoza_rejestru', 'opis': opis, 'podstawa': podstawa}]
    if rejestr and rejestr['stan'] == 'poza_listami':
        opis = f'Płatnik „{platnik}” nie figuruje na żadnej z czterech list firm inwestycyjnych KNF.'
        return [{'modul': 'M1', 'kod': 'platnik_poza_listami', 'opis': opis, 'podstawa': podstawa}]
    return []
