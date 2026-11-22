# Moduł M1: wykrywa opis filmu, który kieruje widzów do usługi finansowej z linkiem lub kodem polecającym
# i nigdzie nie mówi, że to reklama albo płatna współpraca.
#   from polecenia import sygnaly
#   sygnaly('Załóż konto: https://www.trading212.com/join/ABC', {'stan': 'poza_listami', ...}, 'youtube')
#   -> [{'modul': 'M1', 'kod': 'polecenie_bez_oznaczenia', 'opis': '...', 'podstawa': '...'}]
import re
from urllib.parse import parse_qsl, urlsplit

import rejestr

PODSTAWA = (
    'art. 7 pkt 11 ustawy o przeciwdziałaniu nieuczciwym praktykom rynkowym (kryptoreklama), '
    'rekomendacje Prezesa UOKiK w sprawie oznaczania treści reklamowych przez influencerów'
)

LINK = re.compile(r'(?:https?://|www\.)[^\s<>"\'“”„«»()\[\]]+', re.I)

KLUCZE_POLECEN = {
    'ref', 'referral', 'refcode', 'ref_id', 'ref_code', 'referralcode', 'aff', 'affid', 'aff_id', 'affiliate',
    'affiliate_id', 'partner', 'partner_id', 'p_id', 'promo', 'promocode', 'invite', 'invitecode', 'invite_code',
    'code', 'coupon', 'bonus', 'via',
}
MEDIA_POLECEN = {'affiliate', 'referral', 'partner', 'influencer'}
SCIEZKI_POLECEN = {'ref', 'r', 'refer', 'invite', 'referral', 'partner', 'aff', 'go', 'join', 'promocodes', 'promocode'}
PRZEKIEROWANIA = {'track', 'click', 'aff', 'affiliate', 'partners', 'ref', 'invite'}
SIECI_AFILIACYJNE = (
    'awin1.com', 'tradedoubler.com', 'prf.hn', 'pxf.io', 'sjv.io', '7eer.net', 'linksynergy.com', 'shareasale.com',
    'convertiser.com', 'mylead.global',
)
# Własne domeny polecające brokerów nie mają w adresie słowa o poleceniu.
DOMENY_POLECEN = ('geolink.xtb.com', 'link-pso.xtb.com', 'freedom24.club')
# Zaproszenie do czatu, subreddita albo na stronę kanału nie jest poleceniem.
SPOLECZNOSCI = ('youtube.com', 'youtu.be', 'discord.com', 'discord.gg', 't.me', 'whatsapp.com', 'reddit.com', 'patreon.com')

KOD = re.compile(
    r'\b(?:kod(?:em|u|y)?|code)\b'
    r'(?:\s+(?:promocyjn\w*|polecając\w*|rabatow\w*|zniżkow\w*|partnersk\w*|przy rejestracji|moim|mój|my))*'
    r'\s*[:–-]?\s*(?P<cudzyslow>["\'“”„«»]?)(?P<kod>\w{3,20})["\'“”„«»]?',
    re.I,
)
# Słowa pisane wielkimi literami, które w tekstach o finansach stoją po "kod", choć nie są kodem polecającym.
NIE_KODY = {'ISIN', 'BLIK', 'PIN', 'SMS', 'QR', 'LEI', 'SWIFT', 'BIC', 'IBAN', 'CVV', 'PKD'}

FINANSE = re.compile(
    r'\bbroker\w*|\bmakler\w*|\bgiełd\w*|\binwest\w*|\binvest\w*|\btrading\w*|\btrader\w*|\btraduj\w*'
    r'|\bakcje\b|\bakcjami\b|\bdarmow\w+ akcj\w*|\betf\w*|\bstocks?\b|\bshares?\b|\bforex\b|\bcfd\w*'
    r'|\bkrypto\w*|\bcrypto\w*|\bbitcoin\w*|\bbank\w*|\bike\b|\bikze\b|\bobligacj\w*|\bdywidend\w*|\bfundusz\w*'
    r'|\bkantor\w*|\bwalut\w*|\bxtb\b|\bfreedom24\b|\blightyear\b|\brevolut\b|\bibkr\b|\betoro\b|\bdegiro\b|\bsaxo\b'
    r'|\bbinance\b|\bbybit\b|\bmexc\b|\bbingx\b|\bcoinbase\b|\bkraken\b|\bwalutomat\b|\bmbank\b|\bplus500\b'
)
# Fragmenty nazwy hosta, które znaczą usługę finansową: vantagemarkets.com, fusionmarkets.com, gatesfx.com.
HOSTY_FINANSOWE = (
    'trading', 'trader', 'invest', 'broker', 'bank', 'markets', 'forex', 'fx', 'crypto', 'coin', 'stock', 'financ',
    'xtb', 'freedom24', 'lightyear', 'revolut', 'ibkr', 'etoro', 'degiro', 'saxo', 'binance', 'bybit', 'mexc',
    'bingx', 'kraken', 'mbank', 'plus500',
)
# Przelewy, wymiana walut i śledzenie portfela to nie usługi inwestycyjne.
INNE_USLUGI = ('wise.com', 'walutomat.pl', 'myfund.pl', 'parqet.com')
# Zasady oznaczania reklam dotyczą treści kierowanych do odbiorców w Polsce: opis po angielsku im nie podlega.
POLSKIE_LITERY = re.compile(r'[ąćęłńśźż]')
ANGIELSKIE_SLOWA = re.compile(r'\b(?:the|and|you|your|with|this|that|for|from|how|what|get|here|first|are|will)\b')
# Nazwy marek tam, gdzie domena pisze je inaczej niż firma.
NAZWY_MAREK = {
    'xtb': 'XTB', 'etoro': 'eToro', 'trading212': 'Trading 212', 'mexc': 'MEXC', 'ibkr': 'Interactive Brokers',
    'interactivebrokers': 'Interactive Brokers', 'bingx': 'BingX', 'okx': 'OKX', 'degiro': 'DEGIRO', 'mbank': 'mBank',
    'freedom24': 'Freedom24', 'plus500': 'Plus500', 'vantagemarkets': 'Vantage', 'fusionmarkets': 'Fusion Markets',
    'apextraderfunding': 'Apex Trader Funding', 'fundedtradermarkets': 'Funded Trader Markets', 'gatesfx': 'GatesFX',
    'ninjatraderus': 'NinjaTrader',
}
# Porównywarki i rankingi brokerów: link prowadzi do nich, a nie do firmy, której usługę polecają.
POSREDNICY = ('brokerchampion.com', 'twojinteres.pl', 'thefxranker.com', 'tradersunion.com')
STANY = {
    'w_rejestrze': 'w rejestrze KNF', 'spoza_rejestru': 'w rejestrze KNF pod inną spółką', 'mica': 'w rejestrze MiCA',
    'bank': 'bank, poza rejestrami firm inwestycyjnych', 'tfi': 'TFI', 'poza_listami': 'brak w rejestrach KNF i MiCA',
}
# Zniżka na bilet na konferencję o inwestowaniu nie jest poleceniem usługi finansowej.
WYDARZENIE = re.compile(r'bilet\w*|ticket\w*|konferencj\w*|kongres\w*')
_OTOCZENIE = 150

# Samo "prowizja" lub "commission" nie jest oznaczeniem: filmy brokerów ciągle mówią o opłatach.
OZNACZENIE = re.compile(
    r'\brek[li]am\w*|\badvert\w*|\bsponsor\w*|\bwspółprac\w*|\bwspolprac\w*|\bpartnersk\w*|\bpartnerem\b'
    r'|\bpartner\w* (?:odcink\w*|filmu|materiału|kanału)'
    r'|\bafiliac\w*|\baffiliate\w*|\bpolecając\w*|\breferral link|\blokowani\w*|\bpłatn\w+ promocj\w*'
    r'|\bpaid promotion|\bpaid partnership|#ad\b|#sponsored'
    r'|\b(?:i|we) (?:may |might |will |can )?(?:earn|receive|get) (?:\w+ ){0,3}commission'
    r'|\botrzymuj\w* (?:\w+ ){0,3}(?:wynagrodzeni\w*|prowizj\w*)'
)


def w_domenie(host, domeny):
    return any(host == domena or host.endswith('.' + domena) for domena in domeny)


def polecajacy(adres):
    """Prawda, gdy adres niesie polecenie w zapytaniu, ścieżce albo hoście."""
    czesci = urlsplit(adres if '://' in adres else 'https://' + adres)
    host = (czesci.hostname or '').removeprefix('www.')
    if w_domenie(host, SPOLECZNOSCI):
        return False
    for klucz, wartosc in parse_qsl(czesci.query):
        if klucz.lower() in KLUCZE_POLECEN or (klucz.lower() == 'utm_medium' and wartosc.lower() in MEDIA_POLECEN):
            return True
    if SCIEZKI_POLECEN & {czesc.lower() for czesc in czesci.path.split('/')}:
        return True
    return (
        host.split('.')[0] in PRZEKIEROWANIA
        or 'referral' in host or 'affiliate' in host
        or w_domenie(host, SIECI_AFILIACYJNE) or w_domenie(host, DOMENY_POLECEN)
    )


def otoczenie(tekst, trafienie):
    """Linia trafienia i linia nad nią, najwyżej 150 znaków w każdą stronę."""
    # Opisy wymieniają po jednym linku w linii, często pod nagłówkiem z nazwą usługi.
    poczatek_linii = tekst.rfind('\n', 0, trafienie.start())
    poczatek = max(tekst.rfind('\n', 0, max(poczatek_linii, 0)) + 1, trafienie.start() - _OTOCZENIE)
    koniec_linii = tekst.find('\n', trafienie.end())
    koniec = min(len(tekst) if koniec_linii < 0 else koniec_linii, trafienie.end() + _OTOCZENIE)
    return tekst[poczatek:koniec].casefold()


def finansowy(tekst, trafienie, host=''):
    if any(slowo in host for slowo in HOSTY_FINANSOWE):
        return True
    # Liczą się tylko słowa: ścieżka i zapytanie linku nazywają to, co wybrał jego właściciel.
    wokol = LINK.sub(' ', otoczenie(tekst, trafienie))
    return bool(FINANSE.search(wokol)) and not WYDARZENIE.search(wokol)


def kod_polecajacy(trafienie):
    """Prawda, gdy słowo po "kod" wygląda jak kod: w cudzysłowie albo pisane wielkimi literami i nie jest marką."""
    kod = trafienie.group('kod')
    if kod.upper() in NIE_KODY or kod.casefold() in HOSTY_FINANSOWE:
        return False
    return bool(trafienie.group('cudzyslow')) or (kod.upper() == kod and any(znak.isalpha() for znak in kod))


def firma(host):
    """Polecana firma z domeny linku i jej stan w rejestrach: link-pso.xtb.com -> XTB, w_rejestrze."""
    host = host.removeprefix('www.')
    if w_domenie(host, POSREDNICY) or not host.count('.'):
        return None
    # Sieć afiliacyjna nazywa reklamodawcę w poddomenie: ninjatraderus.pxf.io.
    marka = host.split('.')[0] if w_domenie(host, SIECI_AFILIACYJNE) else host.split('.')[-2]
    nazwa = NAZWY_MAREK.get(marka, marka.capitalize())
    wynik = rejestr.sprawdz(nazwa)
    return {'nazwa': nazwa, 'domena': host, 'stan_rejestru': wynik['stan'] if wynik else None}


def sygnal(polecenie, polecana=None):
    opis = f'{polecenie}, a nie ma w nim oznaczenia reklamy ani współpracy. '
    if polecana:
        opis += f'Polecana firma: {polecana["nazwa"]} ({STANY.get(polecana["stan_rejestru"], "nie ustalono w rejestrach")}). '
    opis += 'Oznaczenie mogło paść w samym filmie, więc do sprawdzenia.'
    wynik = {'modul': 'M1', 'kod': 'polecenie_bez_oznaczenia', 'opis': opis, 'podstawa': PODSTAWA}
    if polecana:
        wynik['firma'] = polecana
    return [wynik]


def sygnaly(tekst, rejestr, zrodlo):
    """Jedno ustalenie dla polecenia usługi finansowej w opisie filmu bez oznaczenia."""
    # Firma z rejestrów KNF linkująca własną ofertę nie jest influencerem.
    if zrodlo != 'youtube' or not tekst or (rejestr and rejestr['stan'] != 'poza_listami'):
        return []
    male = LINK.sub(' ', tekst).casefold()
    if len(ANGIELSKIE_SLOWA.findall(male)) >= 3 and len(POLSKIE_LITERY.findall(male)) < 3:
        return []
    # Adresy wycina się najpierw: "partner" lub "ref" wewnątrz linku nie jest oznaczeniem.
    if OZNACZENIE.search(LINK.sub(' ', tekst).casefold()):
        return []
    for trafienie in LINK.finditer(tekst):
        adres = trafienie.group().rstrip('.,;:!?')
        host = urlsplit(adres if '://' in adres else 'https://' + adres).hostname or ''
        if w_domenie(host.removeprefix('www.'), INNE_USLUGI):
            continue
        if polecajacy(adres) and finansowy(tekst, trafienie, host):
            cytat = re.sub(r'^(?:https?://)?(?:www\.)?', '', adres, flags=re.I)
            return sygnal(f'Opis filmu ma link polecający do {host.removeprefix("www.")} („{cytat}”)', firma(host))
    # Linki zastępuje się spacjami tej samej długości, więc pozycje trafień nadal wskazują w oryginalny tekst.
    for trafienie in KOD.finditer(LINK.sub(lambda link: ' ' * len(link.group()), tekst)):
        if kod_polecajacy(trafienie) and finansowy(tekst, trafienie):
            return sygnal(f'Opis filmu podaje kod polecający („{" ".join(trafienie.group().split())}”)')
    return []
