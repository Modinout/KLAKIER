# Moduł M2: sprawdza tekst reklamy firmy inwestycyjnej z regułami UKNF o informacji o ryzyku.
#   from wymogi import sygnaly
#   sygnaly('Zysk 12% rocznie bez wysiłku.', {'stan': 'w_rejestrze', ...})
#   -> [{'modul': 'M2', 'kod': 'zysk_bez_ryzyka', 'opis': '...', 'podstawa': '...'}]
import re

ROZPORZADZENIE = 'rozporządzenia delegowanego 2017/565'

ZYSK = re.compile(
    r'\d+(?:[.,]\d+)?\s*%\s*(?:zysk\w*|zwrot\w*|rocznie|miesięcznie|tygodniowo|dziennie)'
    r'|\bzysk\w* (?:gwarantowan\w+|pewn\w+)|\bgwarantowan\w+ (?:zysk\w*|doch\w+)'
    r'|\bzarob\w*|\bzarabia\w*|\bpasywn\w+ doch\w+|\bguaranteed (?:profits?|returns?)|\bearn (?:up to )?\d'
)
# Odsetki od konta lub lokaty i bonus powitalny nie są zyskiem z inwestowania:
# reguły reklamowe rozporządzenia 2017/565 ich nie obejmują.
ODSETKI = re.compile(r'\blokat\w*|\boprocentowan\w*|\bodset\w*|\boszczędn\w*|\bpromocj\w*|\binterest\b|\bw skali roku')
RYZYKO = re.compile(r'\bryzyk\w*|\bstrat\w*|\butrat\w*|\bstraci\w*|\brisk\w*|\blos[es]\w*')

PODSTAWA_CFD = (
    'Standardowe ostrzeżenie o ryzyku dla kontraktów CFD: decyzja ESMA (UE) 2018/796 z 22 maja 2018 r., '
    'zastąpiona krajową interwencją produktową KNF'
)
CFD = re.compile(r'\bcfd\b|\bkontrakt\w+ na różnic\w+|\bcontracts? for differences?\b|\bforex\b|\bfx\b')
# Samo forex może być kantorem walut; ze słowami o handlu to handel z dźwignią.
HANDEL = re.compile(r'\bhandl\w*|\btrading\w*|\btrade\b|\btraduj\w*|\bdźwigni\w*|\bleverage\b|\bspread\w*|\bbroker\w*')
KANTOR = re.compile(r'\bkantor\w*|\bwymian\w+ walut\w*')
# "74% rachunków inwestorów detalicznych odnotowuje straty", "74% of retail investor accounts lose money",
# oraz krótka forma dozwolona tam, gdzie liczba znaków jest ograniczona.
OSTRZEZENIE_CFD = re.compile(
    r'\d+(?:[.,]\d+)?\s*%[^.!?]{0,120}(?:rachunk\w*|\w*kont\w*|accounts?|cuentas|inwestor\w*|investors?)'
    r'[^.!?]{0,120}(?:strat\w*|trac\w*|los[es]\w*|verlier\w*|pierden)'
    r'|(?:strat\w*|trac\w*|los[es]\w*)[^.!?]{0,120}\d+(?:[.,]\d+)?\s*%[^.!?]{0,60}(?:rachunk\w*|kont\w*|accounts?)'
)

HISTORIA = re.compile(
    r'\bwynik\w* historyczn\w*|\bhistoryczn\w+ (?:wynik\w*|stop\w+ zwrotu)|\bw (?:ostatni\w+|minion\w+) \w+ (?:lat\w*|rok\w*|miesi\w+)'
    r'|\bpast performance|\bhistorical (?:performance|returns)'
)
ZASTRZEZENIE_HISTORII = re.compile(
    r'nie (?:stanowi\w*|są|jest|daj\w+) (?:\w+ ){0,3}(?:gwarancj\w*|wskaźnik\w*)|nie gwarantuj\w*'
    r'|not (?:a )?(?:reliable )?(?:indicator|guarantee)|not indicative|no guarantee'
)

PODATKI = re.compile(r'\bbez podatku|\bulg\w+ podatkow\w+|\bzwrot\w* podatku|\btax[- ]free')
ZASTRZEZENIE_PODATKOW = re.compile(r'indywidualn\w+ sytuacj\w*|zależ\w+ od|(?:może|mogą) ulec zmianie|individual circumstances|may change')

NADZOR = re.compile(r'\bknf\b|komisj\w+ nadzoru finansowego|\bcysec\b|\bfca\b|\bnadzor\w*|\bnadzó\w*|\bregulowan\w*|\blicencjonowan\w*|\bregulated\b')
BEZPIECZENSTWO = re.compile(r'\bbezpiecz\w*|\bgwaran\w*|\bpewn\w+ (?:zysk\w*|inwestycj\w*)|\bsafe\w*|\bsecure\b|\bguarantee\w*')

_ZDANIE = re.compile(r'[^.!?\n]+')
# Zastrzeżenie nazywa rzecz tylko po to, by jej zaprzeczyć: "nie stanowi rekomendacji", "to nie tylko ulgi podatkowe".
_ZAPRZECZENIE = re.compile(r'\bnie\b|\bani\b|\bbez\b|\bżadn\w+|\bnot\b|\bno\b|\bnone\b|\bnothing\b|\bnever\b')
# Liczone w znakach, nie w zdaniach: zastrzeżenia są pełne "art." i "S.A.".
_OKNO = 120


def twierdzenie(wzor, male, przyjmij=lambda trafienie: True):
    """Pierwsze trafienie, któremu nie przeczą słowa przed nim i które przyjmuje wywołujący."""
    for trafienie in wzor.finditer(male):
        if not _ZAPRZECZENIE.search(male[max(0, trafienie.start() - _OKNO):trafienie.start()]) and przyjmij(trafienie):
            return trafienie
    return None


def cytat(tekst, trafienie):
    """Zdanie wokół trafienia, tak jak jest napisane w reklamie."""
    for zdanie in _ZDANIE.finditer(tekst):
        if zdanie.start() <= trafienie.start() < zdanie.end():
            break
    poczatek, koniec = zdanie.start(), zdanie.end()
    # Tekst strony często nie ma kropek: wtedy cytatem są słowa wokół trafienia.
    if koniec - poczatek > 200:
        poczatek, koniec = max(poczatek, trafienie.start() - 80), min(koniec, trafienie.end() + 80)
    return ' '.join(tekst[poczatek:koniec].split())


def sygnal(kod, opis, podstawa):
    return {'modul': 'M2', 'kod': kod, 'opis': opis, 'podstawa': podstawa}


# Opis filmu i strona serwisu firmy nie są reklamami: ostrzeżenie może stać w filmie albo w stopce.
NIE_REKLAMY = ('youtube', 'strony_doradcow')
# Podpis bez linii o ryzyku niczego nie dowodzi: ostrzeżenie zwykle stoi na obrazku, którego tu się nie czyta.
# Tekst, który mówi o ryzyku, a pomija liczbę, to własne skrócone ostrzeżenie reklamodawcy.
MOWA_O_RYZYKU = re.compile(r'\bryzyk\w*|\brisk\w*|\brisiko\w*|\briesgo\w*|\bstracić\b|\butrat\w+ (?:kapitału|pieniędzy|środków)')


def sygnaly(tekst, rejestr, zrodlo=None):
    """Ustalenia o informacji o ryzyku, tylko dla płatnika będącego firmą inwestycyjną z list KNF."""
    if not tekst or not rejestr or rejestr['stan'] not in ('w_rejestrze', 'spoza_rejestru'):
        return []
    male = tekst.casefold()
    wynik = []

    zysk = twierdzenie(ZYSK, male)
    if zysk and not RYZYKO.search(male) and not ODSETKI.search(male):
        wynik.append(sygnal(
            'zysk_bez_ryzyka',
            f'Reklama mówi o zysku („{cytat(tekst, zysk)}”), a nie ma w niej informacji o ryzyku.',
            f'art. 44 ust. 2 lit. b {ROZPORZADZENIE}',
        ))

    cfd = twierdzenie(CFD, male, lambda t: t.group() not in ('forex', 'fx') or (HANDEL.search(male) and not KANTOR.search(male)))
    # Tekst odczytany z obrazu łamie ostrzeżenie na kilka linii.
    o_ryzyku = zrodlo not in NIE_REKLAMY and MOWA_O_RYZYKU.search(male)
    if cfd and o_ryzyku and not OSTRZEZENIE_CFD.search(' '.join(male.split())):
        wynik.append(sygnal(
            'brak_ostrzezenia_cfd',
            f'Reklama oferuje handel kontraktami CFD lub na rynku forex („{cytat(tekst, cfd)}”), wspomina o ryzyku, ale nie podaje, jaki odsetek rachunków klientów traci pieniądze.',
            PODSTAWA_CFD,
        ))

    historia = twierdzenie(HISTORIA, male)
    if historia and not ZASTRZEZENIE_HISTORII.search(male):
        wynik.append(sygnal(
            'wyniki_bez_zastrzezenia',
            f'Reklama podaje wyniki z przeszłości („{cytat(tekst, historia)}”) bez zastrzeżenia, że nie wskazują one przyszłych wyników.',
            f'art. 44 ust. 4 lit. d {ROZPORZADZENIE}',
        ))

    podatki = twierdzenie(PODATKI, male)
    if podatki and not ZASTRZEZENIE_PODATKOW.search(male):
        wynik.append(sygnal(
            'podatki_bez_zastrzezenia',
            f'Reklama odwołuje się do podatków („{cytat(tekst, podatki)}”) bez informacji, że zależą one od sytuacji klienta i mogą się zmienić.',
            f'art. 44 ust. 7 {ROZPORZADZENIE}',
        ))

    for zdanie in _ZDANIE.finditer(male):
        nadzor = NADZOR.search(zdanie.group())
        if nadzor and BEZPIECZENSTWO.search(zdanie.group()):
            miejsce = re.compile(re.escape(nadzor.group())).search(male, zdanie.start())
            wynik.append(sygnal(
                'nadzor_jako_argument',
                f'Reklama łączy nadzór z bezpieczeństwem inwestycji („{cytat(tekst, miejsce)}”).',
                f'art. 44 ust. 8 {ROZPORZADZENIE}',
            ))
            break
    return wynik
