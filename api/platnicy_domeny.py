# Payers compared with the landing domains of their ads: one domain paid for by many payers that are neither listed
# firms nor named after its brand, and a listed brand's name paying for a domain of another brand.
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


def z_marka_domeny(nazwa, domena):
    """True when the name holds the domain's brand; each part of a hyphenated one must be there, as for webull-uk."""
    klucz = bez_znakow(nazwa)
    return all(czesc in klucz for czesc in rdzen_marki(domena).split('-'))


def niezwiazani_platnicy(domena, reklamy):
    """Sorted names of the payers that count; spellings of one name that differ only in case or punctuation are one payer."""
    platnicy = {}
    for reklama in reklamy:
        if reklama['stan'] != 'w_rejestrze' and not z_marka_domeny(reklama['reklamodawca'], domena):
            platnicy.setdefault(bez_znakow(reklama['reklamodawca']), reklama['reklamodawca'].strip())
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


def obca_domena(reklama):
    """Signal when the payer carries the name of a listed brand and the ad leads to a domain without that name."""
    rejestr = reklama['rejestr']
    if not reklama['domena'] or not rejestr or rejestr['stan'] != 'spoza_rejestru':
        return None
    if z_marka_domeny(reklama['reklamodawca'], reklama['domena']):
        return None
    return {
        'modul': 'M1',
        'kod': 'obca_domena',
        'opis': f'Płatnik {reklama["reklamodawca"]} ma nazwę marki z rejestru KNF ({rejestr["podmiot"]}), '
                f'ale reklama prowadzi do domeny {reklama["domena"]}, która tej nazwy nie zawiera.',
        'podstawa': 'nazwa płatnika i domena, do której prowadzi reklama',
    }


def sygnaly_reklamy(reklama, domeny_z_sygnalem):
    """Findings of one ad; domeny_z_sygnalem is the result of sygnaly_domen() over all stored ads."""
    sygnaly = [domeny_z_sygnalem[reklama['domena']]] if reklama['domena'] in domeny_z_sygnalem else []
    obca = obca_domena(reklama)
    return sygnaly + [obca] if obca else sygnaly
