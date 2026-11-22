# Sprawdzenie bramki tematu. Uruchom: docker compose run --rm ai python test_temat.py
import sys
sys.stdout.reconfigure(encoding='utf-8')
from temat import o_inwestycjach, platnik_do_sprawdzenia

OBCY = {'stan': 'poza_listami', 'podmiot': None, 'panstwo': None, 'lista': None}
MARKA = {'stan': 'spoza_rejestru', 'podmiot': 'X Europe Ltd', 'panstwo': 'Cypr', 'lista': 'notyfikowane_zagraniczne'}

# tekst, czy dotyczy inwestowania
TEMATY = [
    ('Lowest spread forex broker', True),
    ('Forex-Investitionskonto mit niedrigen Gebühren', True),
    ('Trade BTC, Gold & Forex in one App', True),
    ('Kup akcje i ETF-y bez prowizji.', True),
    ('Zainwestuj 900 zł i zarabiaj 20 000 zł miesięcznie.', True),
    ('Obligacje oszczędnościowe Skarbu Państwa: jak działają', True),
    ('Lotos daje szansę zarobić 21 000 zł każdemu Polakowi.', True),
    ('kantor.pl najkorzystniejsza platforma wymiany walut', False),
    ('Praca od zaraz, dobre zarobki i umowa o pracę.', False),
    ('Ty masz odpady, ktoś ich szuka. Darmowa giełda odpadów bez pośredników', False),
    ('Szukasz nieruchomości komercyjnej z potencjałem inwestycyjnym? 1 183 m² powierzchni.', False),
    ('Pomagamy bezpiecznie kupić nieruchomość w Tajlandii, od pierwszego kontaktu po odbiór kluczy.', False),
    ('Kurs języka angielskiego online. Zapisz się na pierwszą lekcję za darmo już dziś.', False),
    ('Szukamy kierowców kat. C+E. Praca od zaraz, umowa o pracę, nowe ciągniki.', False),
]
# tekst, płatnik, wynik rejestru, czy ustalenie z rejestru zostaje
PLATNICY = [
    ('', 'Nieznana Sp. z o.o.', OBCY, False),
    ('Revolut Install Install', 'Revolut Ltd', MARKA, True),
    ('Bitpanda Installieren Installieren', 'Bitpanda GmbH', OBCY, False),
    ('Handluj CFD na złocie z dźwignią 1:500', 'Vantage Global Prime Pty Ltd', OBCY, True),
    ('Wybieraj powiadomienia o cenie albo o zmianie w procentach, o resztę zadbamy my. Zainstaluj.', 'FxPro Global Markets Ltd', OBCY, True),
    ('24/7 Mobile Forex App', '上海纬祝网络科技有限公司', OBCY, True),
    ('Virtune XRP ETP jest notowany na Giełdzie Papierów Wartościowych w Warszawie.', 'Virtune', OBCY, False),
    ('Start simulated trading now.', 'FTMO s.r.o', OBCY, False),
    ('Learn valuable skills as a futures trader.', 'Apex Trader Funding', OBCY, False),
    ('Ty masz odpady, ktoś ich szuka. Darmowa giełda odpadów bez pośredników', 'Utylizer.pl', OBCY, False),
    ('Co może się zmienić na rynku mieszkań w Warszawie? Sprawdź, co powstaje w Twojej dzielnicy.', 'natalia_drysiak', OBCY, False),
]
zle = 0
for tekst, oczekiwane in TEMATY:
    dobrze = o_inwestycjach(tekst) == oczekiwane
    zle += not dobrze
    print('OK  ' if dobrze else 'FAIL', tekst[:70].ljust(70), '| expected', oczekiwane)
for tekst, platnik, rejestr, oczekiwane in PLATNICY:
    dobrze = platnik_do_sprawdzenia(tekst, platnik, rejestr) == oczekiwane
    zle += not dobrze
    print('OK  ' if dobrze else 'FAIL', (platnik + ': ' + tekst)[:70].ljust(70), '| expected', oczekiwane)
razem = len(TEMATY) + len(PLATNICY)
print(f'TEMAT {razem - zle} of {razem} passed')
sys.exit(1 if zle else 0)
