# Czy tekst w ogóle dotyczy usług lub instrumentów inwestycyjnych. Ten sam test co o_inwestycjach w
# ai/temat.py, który działa w innej usłudze; zmiana tam wymaga zmiany tutaj.
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
    r'|\bmarkets\b|\bfinancial\b|\bgold\b|\boil\b|\bфорекс\w*|\bинвест\w*|\bзолото\b|\bнефть\b'
)
INWESTOWANIE = re.compile(
    r'\b(?:za)?inwest\w*|\binvest\w*|\bzarabiaj\w*|\bzarobi\w*|\bzysk\w*|\bpomnaż\w*|\bpasywn\w+ doch\w+|\bwypłać\b'
)
# Nieruchomości i towary sprzedaje się tymi samymi czasownikami, ale nie są sprawą nadzoru finansowego.
INNE_RYNKI = re.compile(
    r'\bnieruchomo\w*|\bmieszkan\w*|\bapartament\w*|\bdział\w+ (?:budowlan\w+|roln\w+)|\bgrunt\w*|\bdewelop\w*'
    r'|\bimmobili\w*|\breal estate\b|\bproperty\b|\bodpad\w*|\bzłom\w*|\bsurowc\w+ wtórn\w+'
)


def o_inwestycjach(tekst):
    male = tekst.casefold()
    if INSTRUMENTY.search(male):
        return True
    return bool(INWESTOWANIE.search(male)) and not INNE_RYNKI.search(male)
