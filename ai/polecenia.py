# Module M1: finds a video description that sends viewers to a financial service with a referral link or code
# and says nowhere that it is an ad or a paid cooperation.
#   from polecenia import sygnaly
#   sygnaly('Załóż konto: https://www.trading212.com/join/ABC', {'stan': 'poza_listami', ...}, 'youtube')
#   -> [{'modul': 'M1', 'kod': 'polecenie_bez_oznaczenia', 'opis': '...', 'podstawa': '...'}]
import re
from urllib.parse import parse_qsl, urlsplit

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
# Brokers' own referral domains carry no referral word in the address.
DOMENY_POLECEN = ('geolink.xtb.com', 'link-pso.xtb.com', 'freedom24.club')
# An invite to a chat, a subreddit or a channel page is not a referral.
SPOLECZNOSCI = ('youtube.com', 'youtu.be', 'discord.com', 'discord.gg', 't.me', 'whatsapp.com', 'reddit.com', 'patreon.com')

KOD = re.compile(
    r'\b(?:kod(?:em|u|y)?|code)\b'
    r'(?:\s+(?:promocyjn\w*|polecając\w*|rabatow\w*|zniżkow\w*|partnersk\w*|przy rejestracji|moim|mój|my))*'
    r'\s*[:–-]?\s*(?P<cudzyslow>["\'“”„«»]?)(?P<kod>\w{3,20})["\'“”„«»]?',
    re.I,
)
# Capitalised words that follow "kod" in finance talk without being a referral code.
NIE_KODY = {'ISIN', 'BLIK', 'PIN', 'SMS', 'QR', 'LEI', 'SWIFT', 'BIC', 'IBAN', 'CVV', 'PKD'}

FINANSE = re.compile(
    r'\bbroker\w*|\bmakler\w*|\bgiełd\w*|\binwest\w*|\binvest\w*|\btrading\w*|\btrader\w*|\btraduj\w*'
    r'|\bakcje\b|\bakcjami\b|\bdarmow\w+ akcj\w*|\betf\w*|\bstocks?\b|\bshares?\b|\bforex\b|\bcfd\w*'
    r'|\bkrypto\w*|\bcrypto\w*|\bbitcoin\w*|\bbank\w*|\bike\b|\bikze\b|\bobligacj\w*|\bdywidend\w*|\bfundusz\w*'
    r'|\bkantor\w*|\bwalut\w*|\bxtb\b|\bfreedom24\b|\blightyear\b|\brevolut\b|\bibkr\b|\betoro\b|\bdegiro\b|\bsaxo\b'
    r'|\bbinance\b|\bbybit\b|\bmexc\b|\bbingx\b|\bcoinbase\b|\bkraken\b|\bwalutomat\b|\bmbank\b|\bplus500\b'
)
# Parts of a host name that mark a financial service: vantagemarkets.com, fusionmarkets.com, gatesfx.com.
HOSTY_FINANSOWE = (
    'trading', 'trader', 'invest', 'broker', 'bank', 'markets', 'forex', 'fx', 'crypto', 'coin', 'stock', 'financ',
    'xtb', 'freedom24', 'lightyear', 'revolut', 'ibkr', 'etoro', 'degiro', 'saxo', 'binance', 'bybit', 'mexc',
    'bingx', 'kraken', 'walutomat', 'wise.com', 'mbank', 'plus500', 'myfund', 'parqet',
)
# A discount on a ticket to an investing conference is not a referral to a financial service.
WYDARZENIE = re.compile(r'bilet\w*|ticket\w*|konferencj\w*|kongres\w*')
_OTOCZENIE = 150

# Bare "prowizja" or "commission" is not a disclosure: broker videos talk about fees all the time.
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
    """True when the address carries a referral in its query, its path or its host."""
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
    """The line of the match and the line above it, at most 150 characters each way."""
    # Descriptions list one link per line, often under a heading line that names the service.
    poczatek_linii = tekst.rfind('\n', 0, trafienie.start())
    poczatek = max(tekst.rfind('\n', 0, max(poczatek_linii, 0)) + 1, trafienie.start() - _OTOCZENIE)
    koniec_linii = tekst.find('\n', trafienie.end())
    koniec = min(len(tekst) if koniec_linii < 0 else koniec_linii, trafienie.end() + _OTOCZENIE)
    return tekst[poczatek:koniec].casefold()


def finansowy(tekst, trafienie, host=''):
    if any(slowo in host for slowo in HOSTY_FINANSOWE):
        return True
    # Only the words count: a link's own path or query names whatever its owner chose.
    wokol = LINK.sub(' ', otoczenie(tekst, trafienie))
    return bool(FINANSE.search(wokol)) and not WYDARZENIE.search(wokol)


def kod_polecajacy(trafienie):
    """True when the word after "kod" looks like a code: quoted, or written in capitals, and is not a brand."""
    kod = trafienie.group('kod')
    if kod.upper() in NIE_KODY or kod.casefold() in HOSTY_FINANSOWE:
        return False
    return bool(trafienie.group('cudzyslow')) or (kod.upper() == kod and any(znak.isalpha() for znak in kod))


def sygnal(polecenie):
    opis = (
        f'{polecenie}, a nie ma w nim oznaczenia reklamy ani współpracy. '
        'Oznaczenie mogło paść w samym filmie, więc do sprawdzenia.'
    )
    return [{'modul': 'M1', 'kod': 'polecenie_bez_oznaczenia', 'opis': opis, 'podstawa': PODSTAWA}]


def sygnaly(tekst, rejestr, zrodlo):
    """One finding for a referral to a financial service in a video description with no disclosure."""
    # A firm from the KNF lists linking its own offer is not an influencer.
    if zrodlo != 'youtube' or not tekst or (rejestr and rejestr['stan'] != 'poza_listami'):
        return []
    # Addresses are cut out first: "partner" or "ref" inside a link is not a disclosure.
    if OZNACZENIE.search(LINK.sub(' ', tekst).casefold()):
        return []
    for trafienie in LINK.finditer(tekst):
        adres = trafienie.group().rstrip('.,;:!?')
        host = urlsplit(adres if '://' in adres else 'https://' + adres).hostname or ''
        if polecajacy(adres) and finansowy(tekst, trafienie, host):
            cytat = re.sub(r'^(?:https?://)?(?:www\.)?', '', adres, flags=re.I)
            return sygnal(f'Opis filmu ma link polecający do {host.removeprefix("www.")} („{cytat}”)')
    # Links are blanked to the same length, so match positions still point into the original text.
    for trafienie in KOD.finditer(LINK.sub(lambda link: ' ' * len(link.group()), tekst)):
        if kod_polecajacy(trafienie) and finansowy(tekst, trafienie):
            return sygnal(f'Opis filmu podaje kod polecający („{" ".join(trafienie.group().split())}”)')
    return []
