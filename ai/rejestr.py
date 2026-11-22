# Sprawdza płatnika reklamy na czterech listach firm inwestycyjnych KNF w rejestr_knf.csv,
# potem w rejestrze ESMA dostawców usług w zakresie kryptoaktywów w rejestr_mica.csv.
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

KRAJE = {
    'europe', 'european', 'eu',
    'polska', 'poland', 'pl', 'cyprus', 'cy', 'malta', 'mt', 'ireland', 'ie', 'germany', 'deutschland', 'de',
    'netherlands', 'nl', 'france', 'fr', 'luxembourg', 'lu', 'spain', 'españa', 'es', 'italy', 'austria', 'at',
    'gibraltar', 'gi', 'estonia', 'ee', 'latvia', 'lv', 'lithuania', 'lt', 'bulgaria', 'bg', 'czech', 'cz',
    'slovakia', 'sk', 'liechtenstein', 'denmark', 'dk', 'sweden', 'uk', 'gb', 'us', 'usa', 'au', 'australia',
    'sg', 'singapore', 'hk', 'canada', 'ca', 'seychelles', 'sc', 'bvi', 'ae', 'za',
}

# Słowa odróżniające podmioty jednej marki (eToro Group vs Etoro Europe), a nie marki.
OGOLNE = KRAJE | {
    'global', 'group', 'international', 'int', 'markets', 'market', 'financial', 'finance',
    'services', 'service', 'securities', 'holdings', 'holding', 'operations', 'technology', 'technologies',
}

# Słowa zbyt pospolite, by wskazać jedną firmę: nazwa złożona tylko z nich nie nazywa żadnej marki.
POSPOLITE = {
    'trade', 'trading', 'trader', 'capital', 'invest', 'investment', 'investments', 'prime', 'first', 'alpha',
    'asset', 'assets', 'wealth', 'management', 'partners', 'fx', 'forex', 'bank', 'broker', 'brokers', 'direct',
    'smart', 'best', 'top', 'one', 'money', 'crypto', 'digital', 'union', 'royal', 'swiss',
    'dom', 'maklerski', 'biuro', 'maklerskie', 'departament', 'banku', 'banking', 'inwestycyjny',
}

_FORMA = re.compile(r'\b(?:' + '|'.join(sorted(map(re.escape, FORMY_PRAWNE), key=len, reverse=True)) + r')\b')
_NAWIAS = re.compile(r'\(([^)]*)\)')


def slowa(nazwa):
    # Kropki znikają bez spacji, żeby S.A. i SA czytały się tak samo.
    tekst = re.sub(r'[\W_]+', ' ', nazwa.casefold().replace('.', ''))
    return ' '.join(tekst.split())


def normalizuj(nazwa):
    return ' '.join(_FORMA.sub(' ', slowa(nazwa)).split())


def klucz(nazwa):
    """Nazwa do porównania. Ta złożona tylko z pospolitych słów zachowuje formę prawną: DOM MAKLERSKI INC S.A."""
    n = normalizuj(nazwa)
    if n and set(n.split()) <= POSPOLITE | OGOLNE:
        return slowa(nazwa)
    return n


def nazwy(wpis):
    """Wszystkie nazwy wpisu rejestru: KNF łączy warianty przez ' | ' i drugą pełną nazwę podaje w nawiasie."""
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
    """Ile słów marki mają wspólnych dwa rdzenie nazw, 0 gdy to różne marki."""
    if not a or not b:
        return 0
    krotszy, dluzszy = sorted([a, b], key=lambda r: (len(r), len(r[0])))
    if dluzszy[:len(krotszy)] == krotszy:
        if set(krotszy) <= POSPOLITE:
            return 0
        # Krótkie słowo marki z kolejnym słowem to najczęściej osoba albo inny produkt: tom, beta.
        if len(krotszy) == 1 and len(krotszy[0]) < 5 and len(dluzszy) > 1:
            return 0
        return len(krotszy)
    # Jednowyrazowa marka z doklejonym krajem: plus500 i plus500cy, ale nie revolut i revolution.
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
# Odwrócone, żeby nazwa wymieniona dwa razy wskazywała pierwszy wpis.
_PO_NAZWIE = {nazwa: wpis for wpis, nazwa in reversed(_NAZWY)}

# Marki i krótkie nazwy podmiotów z list. Nazwa z błędem względem rejestru kończy się błędem tutaj, przy imporcie.
with pathlib.Path(__file__).with_name('marki_knf.csv').open(encoding='utf-8', newline='') as _plik:
    _MARKI = {klucz(r['marka']): _PO_NAZWIE[klucz(r['nazwa_w_rejestrze'])] for r in csv.DictReader(_plik, delimiter=';')}

# Dostawcy usług w zakresie kryptoaktywów z zezwoleniem w państwie UE na mocy MiCA, z przejściowego rejestru ESMA.
# Mogą obsługiwać Polskę na tej licencji, więc nie ma ich na listach KNF.
STAN_MICA = '18.11.2026'
with pathlib.Path(__file__).with_name('rejestr_mica.csv').open(encoding='utf-8', newline='') as _plik:
    _MICA = [{'nazwa': r['nazwa'], 'marka': r['marka'], 'panstwo': r['panstwo'], 'lista': 'mica'}
             for r in csv.DictReader(_plik, delimiter=';')]
_MICA_PO_NAZWIE = {klucz(w['nazwa']): w for w in reversed(_MICA)}
# Nazwa handlowa oznacza podmiot z licencją tylko wtedy, gdy płatnik nie podaje formy prawnej: Revolut, a nie Revolut Ltd.
_MICA_PO_MARCE = {klucz(w['marka']): w for w in reversed(_MICA) if klucz(w['marka'])}


def sprawdz(reklamodawca):
    nazwa = klucz(reklamodawca or '')
    if not nazwa:
        return None
    # Marka z krajem to ta sama marka, ale z formą prawną to już inny podmiot: Trading 212 UK Limited.
    marka = None
    if normalizuj(reklamodawca) == slowa(reklamodawca):
        marka = ' '.join(s for s in nazwa.split() if s not in KRAJE)
    wpis = _PO_NAZWIE.get(nazwa) or _MARKI.get(nazwa) or _PO_NAZWIE.get(marka) or _MARKI.get(marka)
    if wpis:
        return wynik('w_rejestrze', wpis)
    # Sama marka nie wskazuje na inną firmę, gdy marka ma jeden podmiot na listach: CMC Markets.
    if marka is not None and rdzen(nazwa) and not set(rdzen(nazwa)) <= POSPOLITE:
        podmioty = {w['nazwa']: w for w, n in reversed(_NAZWY) if rdzen(n) == rdzen(nazwa)}
        if len(podmioty) == 1:
            return wynik('w_rejestrze', *podmioty.values())
    wpis = _MICA_PO_NAZWIE.get(nazwa) or _MICA_PO_NAZWIE.get(marka) or _MICA_PO_MARCE.get(marka)
    if wpis:
        return wynik('mica', wpis)
    # Wśród czterech list nie ma listy TFI, więc towarzystwa funduszy nie da się tu sprawdzić.
    if 'tfi' in nazwa.split() or 'towarzystwo funduszy inwestycyjnych' in nazwa:
        return wynik('tfi')
    najlepszy, ile = None, 0
    for wpis, n in _NAZWY:
        w = wspolne(rdzen(nazwa), rdzen(n))
        if w > ile:
            najlepszy, ile = wpis, w
    if najlepszy:
        return wynik('spoza_rejestru', najlepszy)
    # Cztery listy zawierają firmy inwestycyjne i biura maklerskie banków. Bank bez biura maklerskiego podlega
    # nadzorowi w innym rejestrze, więc nie da się go tu sprawdzić.
    if 'bank' in nazwa.split():
        return wynik('bank')
    return wynik('poza_listami')


# W tych źródłach nazwa to autor materiału, a nie płatnik reklamy: rejestr nie daje ustalenia.
AUTOR_ZAMIAST_PLATNIKA = ('youtube', 'strony_doradcow')


def sygnaly(platnik, rejestr, zrodlo=None):
    """Ustalenia dla analityka: jeden sygnał, gdy płatnika nie ma na listach, w przeciwnym razie żadnego."""
    if zrodlo in AUTOR_ZAMIAST_PLATNIKA:
        return []
    podstawa = f'Listy KNF, stan na {STAN_NA}'
    if rejestr and rejestr['stan'] == 'spoza_rejestru':
        opis = f'Płatnik „{platnik}” nie figuruje w rejestrach KNF. Marka odpowiada wpisowi „{rejestr["podmiot"]}” ({rejestr["panstwo"]}).'
        return [{'modul': 'M1', 'kod': 'platnik_spoza_rejestru', 'opis': opis, 'podstawa': podstawa}]
    if rejestr and rejestr['stan'] == 'poza_listami':
        opis = f'Płatnik „{platnik}” nie figuruje na żadnej z czterech list firm inwestycyjnych KNF ani w rejestrze MiCA (ESMA).'
        podstawa += f'; rejestr MiCA (ESMA), stan na {STAN_MICA}'
        return [{'modul': 'M1', 'kod': 'platnik_poza_listami', 'opis': opis, 'podstawa': podstawa}]
    return []
