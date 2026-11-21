# One landing domain paid for by many payers that are neither listed firms nor named after its brand.
from collections import defaultdict

PROG = 3
NAJWIECEJ_NAZW = 6
# Second-level labels under a country code that name no brand, as in co.uk or com.pl.
OGOLNE = {'co', 'com', 'net', 'org', 'gov', 'edu', 'ac'}


def rdzen_marki(domena):
    czesci = domena.lower().split('.')
    if len(czesci) > 2 and len(czesci[-1]) == 2 and czesci[-2] in OGOLNE:
        return czesci[-3]
    return czesci[-2] if len(czesci) > 1 else czesci[0]


def bez_znakow(tekst):
    return ''.join(znak for znak in tekst.lower() if znak.isalnum())


def niezwiazani_platnicy(domena, reklamy):
    """Sorted names of the payers that count; spellings of one name that differ only in case or punctuation are one payer."""
    rdzen = bez_znakow(rdzen_marki(domena))
    platnicy = {}
    for reklama in reklamy:
        klucz = bez_znakow(reklama['reklamodawca'])
        if reklama['stan'] != 'w_rejestrze' and rdzen not in klucz:
            platnicy.setdefault(klucz, reklama['reklamodawca'].strip())
    return sorted(platnicy.values(), key=str.casefold)


def sygnal(domena, platnicy):
    nazwy = ', '.join(platnicy[:NAJWIECEJ_NAZW])
    if len(platnicy) > NAJWIECEJ_NAZW:
        nazwy += f' i {len(platnicy) - NAJWIECEJ_NAZW} innych'
    return {
        'modul': 'M1',
        'kod': 'wielu_platnikow_domeny',
        'opis': f'Reklamy domeny {domena} opłaca {len(platnicy)} różnych płatników niezwiązanych z marką: {nazwy}.',
        'podstawa': 'reklamy tej domeny zebrane w bazie',
    }


def sygnaly_domen(reklamy):
    """reklamy: domena, reklamodawca and register stan of each ad with both. Returns {domena: signal} for the domains that fire."""
    po_domenie = defaultdict(list)
    for reklama in reklamy:
        po_domenie[reklama['domena']].append(reklama)
    sygnaly = {}
    for domena, reklamy_domeny in po_domenie.items():
        platnicy = niezwiazani_platnicy(domena, reklamy_domeny)
        if len(platnicy) >= PROG:
            sygnaly[domena] = sygnal(domena, platnicy)
    return sygnaly
