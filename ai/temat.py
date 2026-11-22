# Mówi, czy tekst w ogóle dotyczy usług lub instrumentów inwestycyjnych.
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
# Nieruchomości i towary sprzedaje się tymi samymi czasownikami, ale to nie sprawa nadzoru finansowego.
INNE_RYNKI = re.compile(
    r'\bnieruchomo\w*|\bmieszkan\w*|\bapartament\w*|\bdział\w+ (?:budowlan\w+|roln\w+)|\bgrunt\w*|\bdewelop\w*'
    r'|\bimmobili\w*|\breal estate\b|\bproperty\b|\bodpad\w*|\bzłom\w*|\bsurowc\w+ wtórn\w+'
)


def o_inwestycjach(tekst):
    male = tekst.casefold()
    if INSTRUMENTY.search(male):
        return True
    return bool(INWESTOWANIE.search(male)) and not INNE_RYNKI.search(male)


def platnik_do_sprawdzenia(tekst, platnik, rejestr):
    """Czy ustalenie z rejestru o płatniku ma sens dla reklamy z tym tekstem."""
    # Marka, którą rejestr zna pod innym podmiotem, sprzedaje usługi finansowe niezależnie od tego, co mówi reklama.
    if rejestr and rejestr['stan'] == 'spoza_rejestru':
        return True
    # Tekst zbyt krótki, by poznać temat, nie daje ustalenia: brak licencji ma znaczenie tylko dla oferty inwestycyjnej.
    return o_inwestycjach(tekst + ' ' + (platnik or ''))
