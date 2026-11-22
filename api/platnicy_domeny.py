# Płatnicy porównani z domenami docelowymi ich reklam: jedna domena opłacana przez wielu płatników bez licencji z rejestru
# KNF lub MiCA i bez nazwy jej marki, oraz nazwa marki z rejestru płacąca za domenę innej marki.
from collections import defaultdict

from poziom import LICENCJE

PROG = 3
NAJWIECEJ_NAZW = 6
# Etykiety drugiego poziomu pod kodem kraju, które nie nazywają żadnej marki, jak w co.uk czy com.pl.
OGOLNE = {'co', 'com', 'net', 'org', 'gov', 'edu', 'ac'}


def rdzen_marki(domena):
    czesci = domena.lower().split('.')
    if len(czesci) > 2 and len(czesci[-1]) == 2 and czesci[-2] in OGOLNE:
        return czesci[-3]
    return czesci[-2] if len(czesci) > 1 else czesci[0]


def bez_znakow(tekst):
    return ''.join(znak for znak in tekst.lower() if znak.isalnum())


def z_marka_domeny(nazwa, domena):
    """True, gdy nazwa zawiera markę domeny; każda część marki z myślnikiem musi w niej być, jak dla webull-uk."""
    klucz = bez_znakow(nazwa)
    return all(czesc in klucz for czesc in rdzen_marki(domena).split('-'))


def niezwiazani_platnicy(domena, reklamy):
    """Posortowane nazwy płatników, którzy się liczą; zapisy jednej nazwy różniące się tylko wielkością liter
    lub interpunkcją to jeden płatnik."""
    platnicy = {}
    for reklama in reklamy:
        if reklama['stan'] not in LICENCJE and not z_marka_domeny(reklama['reklamodawca'], domena):
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
        'podstawa': 'Reklamy tej domeny zebrane w bazie',
    }


def sygnaly_domen(reklamy):
    """reklamy: domena, reklamodawca i stan z rejestru każdej reklamy mającej oba.
    Zwraca {domena: sygnał} dla domen, które się zapalają."""
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
    """Sygnał, gdy płatnik nosi nazwę marki z rejestru, a reklama prowadzi do domeny bez tej nazwy."""
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
        'podstawa': 'Porównanie nazwy płatnika z domeną, do której prowadzi reklama',
    }


def sygnaly_reklamy(reklama, domeny_z_sygnalem):
    """Ustalenia jednej reklamy; domeny_z_sygnalem to wynik sygnaly_domen() po wszystkich zapisanych reklamach."""
    sygnaly = [domeny_z_sygnalem[reklama['domena']]] if reklama['domena'] in domeny_z_sygnalem else []
    obca = obca_domena(reklama)
    return sygnaly + [obca] if obca else sygnaly
