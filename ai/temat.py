# Tells whether a text is about investment services or instruments at all.
#   from temat import o_inwestycjach
#   o_inwestycjach('Lowest spread forex broker') -> True
#   o_inwestycjach('Giełda odpadów: sprzedaj złom i makulaturę') -> False
import re

INSTRUMENTY = re.compile(
    r'\betf\w*|\bforex\w*|\bcfd\b|\bfx\b|\bkrypto\w*|\bcrypto\w*|\bbitcoin\w*|\bbtc\b|\bethereum\b'
    r'|\bakcj[eiaęo]\b|\bakcjami\b|\bakcjach\b|\bobligacj\w*|\bdywidend\w*|\bkontrakt\w+ (?:terminow\w+|na różnic\w+)'
    r'|\bbroker\w*|\bmakler\w*|\btrading\w*|\btrader\w*|\btraden\b|\bdźwigni\w*|\bspread\w*|\bleverage\b'
    r'|\bgiełd\w+ papierów|\bgpw\b|\bnasdaq\b|\bs&p ?500\b|\bike\b|\bikze\b'
    r'|\b(?:konto|konta|rachunek|rachunku|doradztw\w+|fundusz\w*|portfel\w*|produkt\w*|platform\w+|strategi\w+|sygnał\w*) inwestycyjn\w+'
    r'|\bfundusz\w* (?:akcji|obligacji|etf)|\bzarządzani\w+ (?:majątkiem|aktywami|portfel\w+)|\bfamily office|\bwealth management'
    r'|\bstocks?\b|\bshares\b|\bbonds\b|\bsecurities\b|\binvestment (?:account|advice|fund|platform)|\basset management'
    r'|\baktien\w*|\banleihen\b|\bbörse\w*|\bwertpapier\w*|\binvestitionskonto\b|\bdepot\b'
    r'|\bmarkets\b|\bfinancial\b|\bwymian\w+ walut\w*|\bkantor\w*|\bgold\b|\boil\b|\bфорекс\w*|\bинвест\w*|\bзолото\b|\bнефть\b'
)
INWESTOWANIE = re.compile(
    r'\b(?:za)?inwest\w*|\binvest\w*|\bzarabiaj\w*|\bzysk\w*|\bpomnaż\w*|\bpasywn\w+ doch\w+|\bwypłać\b'
)
# Property and goods are sold with the same verbs but are no business of the financial supervisor.
INNE_RYNKI = re.compile(
    r'\bnieruchomo\w*|\bmieszkan\w*|\bapartament\w*|\bdział\w+ (?:budowlan\w+|roln\w+)|\bgrunt\w*|\bdewelop\w*'
    r'|\bimmobili\w*|\breal estate\b|\bproperty\b|\bodpad\w*|\bzłom\w*|\bsurowc\w+ wtórn\w+'
)


# An image ad read by OCR is often a logo and a button: too little to say what it sells.
ZA_MALO_SLOW = 12


def o_inwestycjach(tekst):
    male = tekst.casefold()
    if INSTRUMENTY.search(male):
        return True
    return bool(INWESTOWANIE.search(male)) and not INNE_RYNKI.search(male)


def platnik_do_sprawdzenia(tekst, platnik, rejestr):
    """Whether a register finding about the payer makes sense for an ad with this text."""
    # A brand that the register knows under another entity sells financial services whatever the ad says.
    if rejestr and rejestr['stan'] == 'spoza_rejestru':
        return True
    return nie_do_oceny(tekst) or o_inwestycjach(tekst + ' ' + (platnik or ''))


def nie_do_oceny(tekst):
    """True when the text is too short to tell its topic and names no other market."""
    return len(tekst.split()) < ZA_MALO_SLOW and not INNE_RYNKI.search(tekst.casefold())
