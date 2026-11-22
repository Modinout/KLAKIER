# Sprawdzenie dopasowania do rejestru KNF. Uruchom: docker compose run --rm ai python test_rejestr.py
import sys
sys.stdout.reconfigure(encoding='utf-8')
from rejestr import sprawdz, sygnaly

PROBY = [
    ('Tickmill Ltd', 'spoza_rejestru', 'Tickmill Europe Ltd'),
    ('Revolut Ltd', 'spoza_rejestru', 'Revolut Securities Europe UAB'),
    ('eToro Group Ltd.', 'spoza_rejestru', 'Etoro (Europe) Ltd'),
    ('Plus500 Ltd', 'spoza_rejestru', 'Plus500CY Ltd'),
    ('CMC Markets', 'w_rejestrze', 'CMC Markets Germany GmbH'),
    ('Interactive Brokers', 'w_rejestrze', 'Interactive Brokers Ireland Ltd'),
    ('Lightyear', 'w_rejestrze', 'Lightyear Europe AS'),
    ('etoro', 'w_rejestrze', 'Etoro (Europe) Ltd'),
    ('Interactive Brokers LLC', 'spoza_rejestru', 'Interactive Brokers Ireland Ltd'),
    ('Webull Financial LLC', 'spoza_rejestru', 'Webull'),
    ('Robinhood Markets, Inc', 'spoza_rejestru', 'Robinhood'),
    ('Dom Maklerski Banku Ochrony Środowiska SA', 'w_rejestrze', 'DOM MAKLERSKI BANKU OCHRONY ŚRODOWISKA S.A.'),
    ('BANK POLSKA KASA OPIEKI - SPÓŁKA AKCYJNA', 'w_rejestrze', 'BANK PEKAO S.A.'),
    ('NWAI Dom Maklerski', 'w_rejestrze', 'NWAI DOM MAKLERSKI S.A.'),
    ('AKCENTA CZ a.s.', 'w_rejestrze', 'AKCENTA CZ, a.s.'),
    ('DOM MAKLERSKI INC S.A.', 'w_rejestrze', 'DOM MAKLERSKI INC S.A.'),
    ('Dom Maklerski BOŚ', 'w_rejestrze', 'DOM MAKLERSKI BANKU OCHRONY ŚRODOWISKA S.A.'),
    ('DM BOŚ', 'w_rejestrze', 'DOM MAKLERSKI BANKU OCHRONY ŚRODOWISKA S.A.'),
    ('PKO BP', 'w_rejestrze', 'POWSZECHNA KASA OSZCZĘDNOŚCI BANK POLSKI'),
    ('PKO Bank Polski', 'w_rejestrze', 'POWSZECHNA KASA OSZCZĘDNOŚCI BANK POLSKI'),
    ('Biuro Maklerskie PKO BP', 'w_rejestrze', 'POWSZECHNA KASA OSZCZĘDNOŚCI BANK POLSKI'),
    ('Pekao', 'w_rejestrze', 'BANK POLSKA KASA OPIEKI'),
    ('Bank Pekao', 'w_rejestrze', 'BANK POLSKA KASA OPIEKI'),
    ('XTB', 'w_rejestrze', 'XTB S.A.'),
    ('Biuro maklerskie mBanku', 'w_rejestrze', 'mBANK S.A.'),
    ('mBank S.A. (Biuro Maklerskie mBanku)', 'w_rejestrze', 'mBANK S.A.'),
    ('Bitpanda GmbH', 'mica', 'Bitpanda GmbH'),
    ('Bybit EU GmbH', 'mica', 'Bybit EU GmbH'),
    ('Bybit', 'mica', 'Bybit EU GmbH'),
    ('Saxo Bank', 'bank', None),
    ('Saxo Bank A/S', 'bank', None),
    ('Dom Maklerski', 'poza_listami', None),
    ('Biuro Maklerskie', 'poza_listami', None),
    ('Bank', 'bank', None),
    ('Investments Capital Group', 'poza_listami', None),
    ('Trading Markets Finance', 'poza_listami', None),
    ('Securities Ltd', 'poza_listami', None),
    ('FTMO s.r.o', 'poza_listami', None),
    ('Bybit Technology Limited', 'spoza_rejestru', 'Bybit EU GmbH'),
    ('Trade Republic Bank GmbH', 'mica', 'Trade Republic Bank GmbH'),
    ('Comdirect Bank GmbH', 'bank', None),
    ('Revolution Trading Ltd', 'poza_listami', None),
    ('Erste Towarzystwo Funduszy Inwestycyjnych S.A.', 'tfi', None),
    ('Tom Crosshill', 'poza_listami', None),
    ("Tom's Personal Finance", 'poza_listami', None),
    ('BETA ETF', 'poza_listami', None),
    ('XTB Polska', 'w_rejestrze', 'XTB S.A.'),
    ('ING Polska', 'w_rejestrze', 'ING BANK ŚLĄSKI S.A.'),
    ('Finax Polska', 'w_rejestrze', 'Finax, o.c.p., a.s.'),
    ('Trading 212 UK Limited', 'spoza_rejestru', 'Trading 212 EU GmbH'),
]
zle = 0
for platnik, stan, podmiot in PROBY:
    w = sprawdz(platnik)
    dobrze = w['stan'] == stan and (podmiot in w['podmiot'] if podmiot else w['podmiot'] is None)
    zle += not dobrze
    print('OK  ' if dobrze else 'FAIL', platnik.ljust(48), '| expected', stan.ljust(15), '| got', w['stan'].ljust(15), '|', w['podmiot'])
for pusty in ['', None]:
    dobrze = sprawdz(pusty) is None
    zle += not dobrze
    print('OK  ' if dobrze else 'FAIL', repr(pusty).ljust(48), '| expected None', '| got', sprawdz(pusty))
ZRODLA = [('google_ads', 1), ('youtube', 0), ('strony_doradcow', 0)]
for nazwa in ['Kanał o inwestowaniu', 'Revolut Ltd']:
    for zrodlo, ile in ZRODLA:
        dobrze = len(sygnaly(nazwa, sprawdz(nazwa), zrodlo)) == ile
        zle += not dobrze
        print('OK  ' if dobrze else 'FAIL', (nazwa + ', source ' + zrodlo).ljust(48), '| expected', ile, 'signal(s)')
dobrze = sygnaly('Bitpanda GmbH', sprawdz('Bitpanda GmbH'), 'google_ads') == []
zle += not dobrze
print('OK  ' if dobrze else 'FAIL', 'Bitpanda GmbH (MiCA), source google_ads'.ljust(48), '| expected 0 signals')
razem = len(PROBY) + 2 + 2 * len(ZRODLA) + 1
print('REJESTR', razem - zle, 'of', razem, 'passed')
sys.exit(1 if zle else 0)
