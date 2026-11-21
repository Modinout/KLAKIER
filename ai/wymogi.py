# Module M2: checks the text of an investment firm's own ad against the UKNF rules on risk information.
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
# Interest on an account or a deposit and a welcome bonus are not gains from investing:
# the advertising rules of regulation 2017/565 do not cover them.
ODSETKI = re.compile(r'\blokat\w*|\boprocentowan\w*|\bodset\w*|\boszczędn\w*|\bpromocj\w*|\binterest\b|\bw skali roku')
RYZYKO = re.compile(r'\bryzyk\w*|\bstrat\w*|\butrat\w*|\bstraci\w*|\brisk\w*|\blos[es]\w*')

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
# A disclaimer names a thing only to deny it: "nie stanowi rekomendacji", "to nie tylko ulgi podatkowe".
_ZAPRZECZENIE = re.compile(r'\bnie\b|\bani\b|\bbez\b|\bżadn\w+|\bnot\b|\bno\b|\bnone\b|\bnothing\b|\bnever\b')
# Counted in characters, not sentences: disclaimers are full of "art." and "S.A.".
_OKNO = 120


def twierdzenie(wzor, male, przyjmij=lambda trafienie: True):
    """The first match that the words before it do not deny and that the caller accepts."""
    for trafienie in wzor.finditer(male):
        if not _ZAPRZECZENIE.search(male[max(0, trafienie.start() - _OKNO):trafienie.start()]) and przyjmij(trafienie):
            return trafienie
    return None


def cytat(tekst, trafienie):
    """The sentence around a match, as written in the ad."""
    for zdanie in _ZDANIE.finditer(tekst):
        if zdanie.start() <= trafienie.start() < zdanie.end():
            break
    poczatek, koniec = zdanie.start(), zdanie.end()
    # Page text often has no full stops: then the quote is the words around the match.
    if koniec - poczatek > 200:
        poczatek, koniec = max(poczatek, trafienie.start() - 80), min(koniec, trafienie.end() + 80)
    return ' '.join(tekst[poczatek:koniec].split())


def sygnal(kod, opis, podstawa):
    return {'modul': 'M2', 'kod': kod, 'opis': opis, 'podstawa': podstawa}


def sygnaly(tekst, rejestr):
    """Findings on the risk information, only for a payer that is an investment firm from the KNF lists."""
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
