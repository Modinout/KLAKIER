# Check of the M2 and M3 text rules. Run: docker compose run --rm ai python test_wymogi.py
import sys
sys.stdout.reconfigure(encoding='utf-8')
import doradztwo
import wymogi

FIRMA = {'stan': 'w_rejestrze', 'podmiot': 'DOM MAKLERSKI X S.A.', 'panstwo': 'Polska', 'lista': 'domy_maklerskie'}
MARKA = {'stan': 'spoza_rejestru', 'podmiot': 'X Europe Ltd', 'panstwo': 'Cypr', 'lista': 'notyfikowane_zagraniczne'}
OBCY = {'stan': 'poza_listami', 'podmiot': None, 'panstwo': None, 'lista': None}

# text, register result, expected codes
PROBY = [
    ('Zyskaj 12% rocznie na naszym portfelu.', FIRMA, ['zysk_bez_ryzyka']),
    ('Zyskaj 12% rocznie. Inwestowanie wiąże się z ryzykiem utraty kapitału.', FIRMA, []),
    ('Earn up to 7% a month with our signals.', MARKA, ['zysk_bez_ryzyka']),
    ('Zyskaj aż do 7% oprocentowania wolnych środków.', FIRMA, []),
    ('Otwórz konto i zyskaj do 1100 zł w promocji i do 8% na lokacie.', FIRMA, []),
    ('Twoje oszczędności pracują u nas na 5,3% w skali roku.', FIRMA, []),
    ('Inwestuj z ulgą podatkową. Ulgi podatkowe zależą od spełnienia warunków ustawowych.', FIRMA, []),
    ('Fundusz zarobił 40% w ostatnich 3 latach. Inwestycje wiążą się z ryzykiem.', FIRMA, ['wyniki_bez_zastrzezenia']),
    ('Wyniki historyczne: 40%. Nie stanowią one gwarancji przyszłych wyników. Ryzyko straty.', FIRMA, []),
    ('Past performance is not indicative of future results. Your capital is at risk.', MARKA, []),
    ('Inwestuj bez podatku Belki na IKE.', FIRMA, ['podatki_bez_zastrzezenia']),
    ('Inwestuj bez podatku Belki. Korzyści zależą od indywidualnej sytuacji klienta i mogą ulec zmianie.', FIRMA, []),
    ('Nasza inwestycja jest w pełni bezpieczna, spełniamy wymogi nadzorcze KNF.', FIRMA, ['nadzor_jako_argument']),
    ('Podlegamy nadzorowi KNF. Otwórz rachunek maklerski.', FIRMA, []),
    ('Zyskaj 12% rocznie na naszym portfelu.', OBCY, []),
    ('Zyskaj 12% rocznie na naszym portfelu.', None, []),
    ('', FIRMA, []),
    ('Oferujemy family office dla zamożnych rodzin i zarządzanie majątkiem od 1 mln zł.', OBCY, ['doradztwo_bez_zezwolenia']),
    ('Dołącz do grupy i otrzymuj codzienne sygnały tradingowe na Telegramie.', OBCY, ['doradztwo_bez_zezwolenia']),
    ('We offer wealth management for founders.', None, ['doradztwo_bez_zezwolenia']),
    ('Family Office - Obsługa prawna Warszawa - mklegal Umów konsultacje Home O Kancelarii Oferta Kontakt', OBCY, []),
    ('Kancelaria oferuje obsługę prawną family office i fundacji rodzinnych.', OBCY, []),
    ('Home Oferta Family Office Asset Management Insurance Travel About Us Contact', OBCY, []),
    ('Konto Przekorzystne. Do 5,7% w skali roku na koncie oszczędnościowym.', FIRMA, []),
    ('Do 5,7% w skali roku', FIRMA, []),
    ('Indywidualne doradztwo inwestycyjne dla klientów private banking.', FIRMA, []),
    ('Indywidualne doradztwo inwestycyjne.', MARKA, []),
    ('Film ma charakter edukacyjny i nie jest to doradztwo inwestycyjne.', OBCY, []),
    ('Nothing in this video should be deemed as financial or investment advice.', OBCY, []),
    ('Kupiłem ETF na cały świat i trzymam.', OBCY, []),
    (
        'Ta publikacja handlowa nie stanowi rekomendacji inwestycyjnej ani informacji rekomendującej lub sugerującej '
        'strategię inwestycyjną w rozumieniu Rozporządzenia Parlamentu Europejskiego i Rady (UE) nr 596/2014 z dnia '
        '16 kwietnia 2014 r. w sprawie nadużyć na rynku, uzupełnionego w odniesieniu do środków technicznych do celów '
        'obiektywnej prezentacji rekomendacji inwestycyjnych.', OBCY, [],
    ),
    ('Materiał nie stanowi porady ani doradztwa inwestycyjnego w rozumieniu art. 76 ustawy.', OBCY, []),
    ('To nie jest porada inwestycyjna, nie jest rekomendacją kupna ani sprzedaży.', OBCY, []),
    ('Treści nie należy traktować jako doradztwa inwestycyjnego.', OBCY, []),
    ('Nasze analizy nie są poradą. To nie są sygnały inwestycyjne.', OBCY, []),
    ('You should consult a qualified professional when seeking out investment advice.', OBCY, []),
    ('03:23 Zarządzanie portfelem i sprzedaż akcji', OBCY, []),
    ('Przeciętny inwestor nie uzyskuje nawet połowy potencjalnej stopy zwrotu z portfela.', FIRMA, []),
    ('IKE i IKZE to nie tylko ulgi podatkowe.', FIRMA, []),
    ('Podatek Belki to 19% Twoich zysków. Dołącz do społeczności i zyskaj przewagę.', FIRMA, []),
]
zle = 0
for tekst, rejestr, kody in PROBY:
    sygnaly = wymogi.sygnaly(tekst, rejestr) + doradztwo.sygnaly(tekst, rejestr)
    mam = [s['kod'] for s in sygnaly]
    dobrze = mam == kody and all(s['modul'] in ('M2', 'M3') and s['opis'] and s['podstawa'] for s in sygnaly)
    zle += not dobrze
    print('OK  ' if dobrze else 'FAIL', tekst[:60].ljust(60), '| expected', kody, '| got', mam)

cytat = wymogi.sygnaly('Konto z bonusem. Zyskaj 12% rocznie na portfelu. Zadzwoń.', FIRMA)[0]['opis']
dobrze = '„Zyskaj 12% rocznie na portfelu”' in cytat
zle += not dobrze
print('OK  ' if dobrze else 'FAIL', 'the finding quotes the sentence as written |', cytat)

print(f'{len(PROBY) + 1 - zle} of {len(PROBY) + 1} checks passed')
sys.exit(1 if zle else 0)
