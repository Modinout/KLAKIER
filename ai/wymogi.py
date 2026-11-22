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

# Pełny okres pięciu lat, okres odniesienia albo źródło danych.
OKRES_HISTORII = re.compile(r'\b(?:5|pięć|pięciu) lat\w*|\b60 miesięcy|\bokres\w* (?:referencyjn|odniesieni)\w*|\bźródł\w*|\bsource\b|\b5 years\b')
OPLATY = re.compile(r'\bprowizj\w*|\bopłat\w*|\bkoszt\w*|\bfees?\b|\bcharges\b|\bcosts?\b')
OBCA_WALUTA = re.compile(r'\busd\b|\beur\b|\bchf\b|\bgbp\b|\$|€|\bdolar\w*|\beuro\b')
KURS_WALUTY = re.compile(r'\bkurs\w* walut\w*|\bzmian\w+ kurs\w*|\bryzyk\w* walutow\w*|\bexchange rate|\bcurrency (?:risk|fluctuation)')
PROGNOZA = re.compile(
    r'\bprognoz\w*|\bprzewidywan\w+ (?:zysk\w*|wzrost\w*|stop\w*|wynik\w*)'
    r'|\bcen\w+ docelow\w*|\bforecast\w*|\bexpected returns?|\btarget price'
    r'|\b(?:wzrośnie|wzrosną|spadnie|osiągnie|podwoi)\b'
)
ZASTRZEZENIE_PROGNOZY = re.compile(ZASTRZEZENIE_HISTORII.pattern + r'|prognoz\w* (?:nie|mogą się nie)|forecasts? (?:are|is) not')
# Zdanie ostrzeżenia, którego przeciętny odbiorca nie przeczyta: bardzo długie albo pełne długich słów.
# Standardowe ostrzeżenie ESMA o CFD ma około 30 słów, więc próg leży wyraźnie wyżej.
NAJWIECEJ_SLOW_OSTRZEZENIA = 45
DLUGIE_SLOWO = 13
# Ostrzeżenie po angielsku w polskiej reklamie: polski przekaz rozpoznaje się po częstych słowach.
POLSKIE_SLOWA = re.compile(r'\b(?:się|jest|nie|dla|oraz|już|dziś|twoje?|twój|nasz\w*|inwestuj\w*|kont[ao]|koncie|zł)\b')
RYZYKO_PL = re.compile(r'\bryzyk\w*|\bstrat\w*|\butrat\w*|\bstraci\w*')
RYZYKO_EN = re.compile(r'\brisk\w*|\blose money|\bloss(?:es)?\b')

POROWNANIE = re.compile(
    r'\blepsz\w* (?:niż|od)\b|\bw porównaniu (?:z|do)\b|\bnajtańsz\w*|\bnajniższ\w* (?:prowizj|opłat|spread|koszt)\w*'
    r'|\bnajlepsz\w* (?:broker|platform|aplikacj|kont)\w*|\bnr ?1\b|\bnumer jeden\b'
    r'|\bcheapest\b|\blowest (?:fees|spreads?|commissions?|costs?)\b|\bbetter than\b|\bcompared (?:to|with)\b'
    r'|\bbest (?:broker|platform|app|trading)\w*|\bvs\.?\s'
)
# Podstawa porównania: źródło, ranking, data albo okres.
PODSTAWA_POROWNANIA = re.compile(r'\bźródł\w*|\bsource\b|\bwedług\b|\bna podstawie\b|\bstan na\b|\bas (?:of|at)\b|\bbased on\b'
                                 r'|\branking\w*|\bbadani\w*|\bsurvey\b|\b(?:19|20)\d{2}\b')

PODATKI = re.compile(r'\bbez podatku|\bulg\w+ podatkow\w+|\bzwrot\w* podatku|\btax[- ]free')
ZASTRZEZENIE_PODATKOW = re.compile(r'indywidualn\w+ sytuacj\w*|zależ\w+ od|(?:może|mogą) ulec zmianie|individual circumstances|may change')

NADZOR = re.compile(r'\bknf\b|komisj\w+ nadzoru finansowego|\bcysec\b|\bfca\b|\bnadzor\w*|\bnadzó\w*|\bregulowan\w*|\blicencjonowan\w*|\bregulated\b')
BEZPIECZENSTWO = re.compile(r'\bbezpiecz\w*|\bgwaran\w*|\bpewn\w+ (?:zysk\w*|inwestycj\w*)|\bsafe\w*|\bsecure\b|\bguarantee\w*'
                            r'|\bzatwierdz\w*|\bzaakceptowan\w*|\baprob\w*|\bpoleca\w*|\brekomend\w*|\bapproved\b|\bendorsed\b')

_ZDANIE = re.compile(r'[^.!?\n]+')
# Zastrzeżenie nazywa rzecz tylko po to, by jej zaprzeczyć: "nie stanowi rekomendacji", "to nie tylko ulgi podatkowe".
_ZAPRZECZENIE = re.compile(r'\bnie\b|\bani\b|\bbez\b|\bżadn\w+|\bnot\b|\bno\b|\bnone\b|\bnothing\b|\bnever\b')
# Liczone w znakach, nie w zdaniach: zastrzeżenia są pełne "art." i "S.A.".
_OKNO = 120
_POWTORZENIE = re.compile(r'(\S.{14,}?) \1(?= |$)')


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
    przed = po = ''
    # Tekst strony często nie ma kropek: wtedy cytatem są całe słowa wokół trafienia.
    if koniec - poczatek > 200:
        od, do = max(poczatek, trafienie.start() - 80), min(koniec, trafienie.end() + 80)
        if od > poczatek:
            od, przed = tekst.find(' ', od, trafienie.start()) + 1 or od, '…'
        if do < koniec:
            spacja = tekst.rfind(' ', trafienie.end(), do)
            do, po = (spacja if spacja > 0 else do), '…'
        poczatek, koniec = od, do
    slowa = ' '.join(tekst[poczatek:koniec].split())
    # Strony powtarzają tytuł obok siebie; w cytacie wystarczy raz.
    return przed + _POWTORZENIE.sub(r'\1', slowa) + po


def zdanie_z(tekst, trafienie):
    for zdanie in _ZDANIE.finditer(tekst):
        if zdanie.start() <= trafienie.start() < zdanie.end():
            return zdanie.group()
    return ''


def sygnal(kod, opis, podstawa):
    return {'modul': 'M2', 'kod': kod, 'opis': opis, 'podstawa': podstawa}


# Opis filmu i strona serwisu firmy nie są reklamami: ostrzeżenie może stać w filmie albo w stopce.
NIE_REKLAMY = ('youtube', 'strony_doradcow')
# Podpis bez linii o ryzyku niczego nie dowodzi: ostrzeżenie zwykle stoi na obrazku, którego tu się nie czyta.
# Tekst, który mówi o ryzyku, a pomija liczbę, to własne skrócone ostrzeżenie reklamodawcy.
MOWA_O_RYZYKU = re.compile(r'\bryzyk\w*|\brisk\w*|\brisiko\w*|\briesgo\w*|\bstracić\b|\butrat\w+ (?:kapitału|pieniędzy|środków)')


def sygnaly(tekst, rejestr, zrodlo=None):
    """Ustalenia o informacji o ryzyku, tylko dla płatnika będącego firmą inwestycyjną z rejestrów KNF."""
    if not tekst or not rejestr or rejestr['stan'] not in ('w_rejestrze', 'spoza_rejestru'):
        return []
    male = tekst.casefold()
    wynik = []

    zysk = twierdzenie(ZYSK, male)
    if zysk and not RYZYKO.search(male) and not ODSETKI.search(male):
        wynik.append(sygnal(
            'zysk_bez_ryzyka',
            f'Reklama mówi o zysku („{cytat(tekst, zysk)}”), a nie ma w niej informacji o ryzyku.',
            f'art. 44 ust. 2 lit. b {ROZPORZADZENIE}; kryterium UKNF nr 3',
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
            f'art. 44 ust. 4 lit. d {ROZPORZADZENIE}; kryterium UKNF nr 14',
        ))

    # Okres i opłaty dotyczą podanych liczb; samo zastrzeżenie o wynikach z przeszłości ich nie wymaga.
    liczby = historia and re.search(r'\d\s*%', zdanie_z(male, historia))
    if liczby and not OKRES_HISTORII.search(male):
        wynik.append(sygnal(
            'wyniki_bez_okresu',
            f'Reklama podaje wyniki z przeszłości („{cytat(tekst, historia)}”) bez okresu pięciu lat, okresu odniesienia ani źródła danych.',
            f'art. 44 ust. 4 lit. b i c {ROZPORZADZENIE}; kryterium UKNF nr 12a',
        ))
    if liczby and (not OPLATY.search(male) or (OBCA_WALUTA.search(male) and not KURS_WALUTY.search(male))):
        brak = 'wpływu prowizji i opłat' if not OPLATY.search(male) else 'ostrzeżenia o wpływie kursu walut'
        wynik.append(sygnal(
            'wyniki_bez_oplat_i_waluty',
            f'Reklama podaje wyniki z przeszłości („{cytat(tekst, historia)}”) bez {brak}.',
            f'art. 44 ust. 4 lit. e i f {ROZPORZADZENIE}; kryterium UKNF nr 12b',
        ))

    # Prognoza to liczba o przyszłości; samo słowo „prognozy” w zaproszeniu do obserwowania nią nie jest.
    prognoza = twierdzenie(PROGNOZA, male, lambda t: re.search(r'\d', zdanie_z(male, t)))
    if prognoza and not ZASTRZEZENIE_PROGNOZY.search(male):
        wynik.append(sygnal(
            'prognoza_bez_zastrzezenia',
            f'Reklama podaje prognozę („{cytat(tekst, prognoza)}”) bez zastrzeżenia, że nie jest ona wiarygodnym wskaźnikiem przyszłych wyników.',
            f'art. 44 ust. 6 {ROZPORZADZENIE}; kryterium UKNF nr 15',
        ))

    if len(POLSKIE_SLOWA.findall(male)) >= 3 and RYZYKO_EN.search(male) and not RYZYKO_PL.search(male):
        wynik.append(sygnal(
            'ryzyko_w_innym_jezyku',
            f'Reklama jest po polsku, a informacja o ryzyku po angielsku („{cytat(tekst, RYZYKO_EN.search(male))}”).',
            f'art. 44 ust. 2 lit. f {ROZPORZADZENIE}; kryterium UKNF nr 10',
        ))

    # Tekst strony i opis filmu często nie mają kropek, więc ich „zdaniem” bywa całe menu.
    for zdanie in _ZDANIE.finditer(tekst if zrodlo not in NIE_REKLAMY else ''):
        slowa = zdanie.group().split()
        dlugie = sum(len(s.strip('.,;:()')) >= DLUGIE_SLOWO for s in slowa)
        if RYZYKO_PL.search(zdanie.group().casefold()) and (len(slowa) > NAJWIECEJ_SLOW_OSTRZEZENIA or (len(slowa) > 20 and dlugie > 0.25 * len(slowa))):
            wynik.append(sygnal(
                'ostrzezenie_niezrozumiale',
                f'Ostrzeżenie o ryzyku jest trudne do przeczytania: {len(slowa)} słów w jednym zdaniu, {dlugie} bardzo długich („{cytat(tekst, zdanie)}”).',
                f'art. 44 ust. 2 lit. d {ROZPORZADZENIE}; kryterium UKNF nr 9',
            ))
            break

    porownanie = twierdzenie(POROWNANIE, male)
    if porownanie and not PODSTAWA_POROWNANIA.search(male):
        wynik.append(sygnal(
            'porownanie_bez_podstawy',
            f'Reklama porównuje ofertę („{cytat(tekst, porownanie)}”) bez źródła, założeń ani okresu porównania.',
            f'art. 44 ust. 3 {ROZPORZADZENIE}; kryterium UKNF nr 11',
        ))
    podatki = twierdzenie(PODATKI, male)
    if podatki and not ZASTRZEZENIE_PODATKOW.search(male):
        wynik.append(sygnal(
            'podatki_bez_zastrzezenia',
            f'Reklama odwołuje się do podatków („{cytat(tekst, podatki)}”) bez informacji, że zależą one od sytuacji klienta i mogą się zmienić.',
            f'art. 44 ust. 7 {ROZPORZADZENIE}; kryterium UKNF nr 16',
        ))

    for zdanie in _ZDANIE.finditer(male):
        nadzor = NADZOR.search(zdanie.group())
        if nadzor and BEZPIECZENSTWO.search(zdanie.group()):
            miejsce = re.compile(re.escape(nadzor.group())).search(male, zdanie.start())
            wynik.append(sygnal(
                'nadzor_jako_argument',
                f'Reklama łączy nadzór z bezpieczeństwem inwestycji („{cytat(tekst, miejsce)}”).',
                f'art. 44 ust. 8 {ROZPORZADZENIE}; kryteria UKNF nr 17 i 18',
            ))
            break
    return wynik
