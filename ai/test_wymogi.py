# Sprawdzenie reguł tekstowych M2 i M3. Uruchom: docker compose run --rm ai python test_wymogi.py
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')
import doradztwo
import wymogi

FIRMA = {'stan': 'w_rejestrze', 'podmiot': 'DOM MAKLERSKI X S.A.', 'panstwo': 'Polska', 'lista': 'domy_maklerskie'}
MARKA = {'stan': 'spoza_rejestru', 'podmiot': 'X Europe Ltd', 'panstwo': 'Cypr', 'lista': 'notyfikowane_zagraniczne'}
OBCY = {'stan': 'poza_listami', 'podmiot': None, 'panstwo': None, 'lista': None}

# tekst, wynik rejestru, oczekiwane kody
PROBY = [
    ('Zyskaj 12% rocznie na naszym portfelu.', FIRMA, ['zysk_bez_ryzyka']),
    ('Zyskaj 12% rocznie. Inwestowanie wiąże się z ryzykiem utraty kapitału.', FIRMA, []),
    ('Earn up to 7% a month with our signals.', MARKA, ['zysk_bez_ryzyka']),
    ('Zyskaj aż do 7% oprocentowania wolnych środków.', FIRMA, []),
    ('Otwórz konto i zyskaj do 1100 zł w promocji i do 8% na lokacie.', FIRMA, []),
    ('Twoje oszczędności pracują u nas na 5,3% w skali roku.', FIRMA, []),
    ('Inwestuj z ulgą podatkową. Ulgi podatkowe zależą od spełnienia warunków ustawowych.', FIRMA, []),
    ('Fundusz zarobił 40% w ostatnich 3 latach. Inwestycje wiążą się z ryzykiem.', FIRMA,
     ['wyniki_bez_zastrzezenia', 'wyniki_bez_okresu', 'wyniki_bez_oplat_i_waluty']),
    ('Wyniki historyczne za 5 lat: 40% po opłatach. Nie stanowią one gwarancji przyszłych wyników. Ryzyko straty.', FIRMA, []),
    ('Wyniki historyczne za 5 lat: 40% po opłatach, w USD. Nie stanowią one gwarancji przyszłych wyników. Ryzyko straty.', FIRMA,
     ['wyniki_bez_oplat_i_waluty']),
    ('Wyniki historyczne za 5 lat: 40% po opłatach, w USD; zmiany kursu walut wpływają na wynik. Nie stanowią one gwarancji przyszłych wyników. Ryzyko straty.', FIRMA, []),
    ('Nasza prognoza: S&P 500 wzrośnie o 15% do końca roku. Inwestowanie wiąże się z ryzykiem.', FIRMA, ['prognoza_bez_zastrzezenia']),
    ('Nasza prognoza: S&P 500 wzrośnie o 15%. Prognozy nie są wiarygodnym wskaźnikiem przyszłych wyników. Ryzyko straty.', FIRMA, []),
    ('Inwestuj w akcje i ETF-y na naszym koncie, już dziś. Your capital is at risk.', FIRMA, ['ryzyko_w_innym_jezyku']),
    ('Inwestuj w akcje i ETF-y na naszym koncie, już dziś. Inwestowanie wiąże się z ryzykiem.', FIRMA, []),
    ('Past performance is not indicative of future results. Your capital is at risk.', MARKA, []),
    ('Inwestuj bez podatku Belki na IKE.', FIRMA, ['podatki_bez_zastrzezenia']),
    ('Inwestuj bez podatku Belki. Korzyści zależą od indywidualnej sytuacji klienta i mogą ulec zmianie.', FIRMA, []),
    ('Nasza inwestycja jest w pełni bezpieczna, spełniamy wymogi nadzorcze KNF.', FIRMA, ['nadzor_jako_argument']),
    ('Podlegamy nadzorowi KNF. Otwórz rachunek maklerski.', FIRMA, []),
    ('Produkt zatwierdzony przez KNF. Otwórz rachunek maklerski.', FIRMA, ['nadzor_jako_argument']),
    ('Najtańszy broker w Polsce. Otwórz konto i handluj akcjami. Inwestowanie wiąże się z ryzykiem.', FIRMA, ['porownanie_bez_podstawy']),
    ('Najtańszy broker w Polsce według rankingu z 2026 r. Inwestowanie wiąże się z ryzykiem.', FIRMA, []),
    ('Sprawdź naszą najlepszą ofertę pożyczki.', FIRMA, []),
    ('Kontrakty CFD są złożonymi instrumentami i wiążą się z dużym ryzykiem szybkiej utraty pieniędzy z powodu dźwigni finansowej. '
     '74% rachunków inwestorów detalicznych odnotowuje straty pieniężne w wyniku handlu kontraktami CFD u niniejszego dostawcy.', FIRMA, []),
    ('Inwestowanie w instrumenty finansowe, w tym w szczególności w instrumenty pochodne charakteryzujące się wysokim poziomem '
     'dźwigni finansowej, wiąże się z ryzykiem utraty części lub całości zainwestowanych środków, przy czym wyniki historyczne '
     'nie stanowią gwarancji osiągnięcia podobnych wyników w przyszłości, a klient powinien rozważyć, czy rozumie zasady działania '
     'tych instrumentów oraz czy może pozwolić sobie na wysokie ryzyko utraty środków.', FIRMA, ['ostrzezenie_niezrozumiale']),
    ('Handluj kontraktami CFD na akcje i indeksy. Inwestowanie wiąże się z ryzykiem.', FIRMA, ['brak_ostrzezenia_cfd']),
    ('Handluj kontraktami CFD na akcje i indeksy z niskim spreadem.', FIRMA, []),
    ('Handluj na Złocie CFD', FIRMA, []),
    ('Handluj kontraktami CFD na akcje. 74% rachunków inwestorów detalicznych odnotowuje straty w wyniku handlu CFD u tego dostawcy.', FIRMA, []),
    ('Trade forex with tight spreads. 74% of retail investor accounts lose money when trading CFDs with this provider.', MARKA, []),
    ('Trade forex with tight spreads on our platform. Your capital is at risk.', MARKA, ['brak_ostrzezenia_cfd']),
    ('CFD na złoto. 68% rachunków CFD traci pieniądze.', FIRMA, []),
    ('Handel kontraktami CFD\n75% rachunków inwestorów detalicznych\nodnotowuje straty pieniężne w wyniku handlu\nkontraktami CFD u niniejszego dostawcy', FIRMA, []),
    ('CFD-Handel. 75,2 % der Kleinanlegerkonten verlieren Geld beim CFD-Handel mit diesem Anbieter.', MARKA, []),
    ('Trade Index CFDs now. Trading CFDs/FX carries risk and is not suitable for everyone.', MARKA, ['brak_ostrzezenia_cfd']),
    ('Kontrakty na różnice kursowe z dźwignią 1:30. Możesz stracić więcej, niż wpłacisz.', FIRMA, ['brak_ostrzezenia_cfd']),
    ('Kantor internetowy: wymiana walut po kursie forex, bez prowizji.', FIRMA, []),
    ('Kup akcje i ETF-y bez prowizji. To nie są kontrakty CFD.', FIRMA, []),
    ('Handluj kontraktami CFD na akcje i indeksy. Inwestowanie wiąże się z ryzykiem.', OBCY, []),
    ('Zyskaj 12% rocznie na naszym portfelu.', OBCY, []),
    ('Zyskaj 12% rocznie na naszym portfelu.', None, []),
    ('', FIRMA, []),
    ('Oferujemy family office dla zamożnych rodzin i zarządzanie majątkiem od 1 mln zł.', OBCY, ['doradztwo_bez_zezwolenia']),
    ('Dołącz do grupy i otrzymuj codzienne sygnały tradingowe na Telegramie.', OBCY, ['rekomendacje_ogolne']),
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

CFD = 'Handluj kontraktami CFD na akcje i indeksy. Inwestowanie wiąże się z ryzykiem.'
for zrodlo, kody in [('google_ads', ['brak_ostrzezenia_cfd']), ('tiktok_ads', ['brak_ostrzezenia_cfd']), ('youtube', []), ('strony_doradcow', [])]:
    mam = [s['kod'] for s in wymogi.sygnaly(CFD, FIRMA, zrodlo)]
    zle += mam != kody
    print('OK  ' if mam == kody else 'FAIL', f'CFD ad without the warning, source {zrodlo}'.ljust(60), '| expected', kody, '| got', mam)

cytat = wymogi.sygnaly('Konto z bonusem. Zyskaj 12% rocznie na portfelu. Zadzwoń.', FIRMA)[0]['opis']
dobrze = '„Zyskaj 12% rocznie na portfelu”' in cytat
zle += not dobrze
print('OK  ' if dobrze else 'FAIL', 'the finding quotes the sentence as written |', cytat)

dlugi = ('Family Office nowa usługa na polskim rynku Family Office nowa usługa na polskim rynku ' + 'słowo ' * 30
         + 'oferujemy zarządzanie majątkiem dla rodzin ' + 'koniec ' * 40)
wycinek = wymogi.cytat(dlugi, re.search('zarządzanie', dlugi))
slowa_tekstu = set(dlugi.split())
dobrze = wycinek.startswith('…') and wycinek.endswith('…') and all(s in slowa_tekstu for s in wycinek.strip('…').split())
zle += not dobrze
print('OK  ' if dobrze else 'FAIL', 'a long quote is cut at word boundaries and marked with … |', wycinek)
powtorka = wymogi.cytat('Family Office nowa usługa Family Office nowa usługa', re.search('usługa', 'Family Office nowa usługa'))
zle += powtorka != 'Family Office nowa usługa'
print('OK  ' if powtorka == 'Family Office nowa usługa' else 'FAIL', 'a phrase repeated side by side is quoted once |', powtorka)
POCZATKI = [
    ('﻿ Bieżące sygnały giełdowe', 'sygnały', 'Bieżące sygnały giełdowe'),
    ('Sponsored 00:00 Najtańszy fundusz w Polsce', 'fundusz', 'Najtańszy fundusz w Polsce'),
    ('Zobacz http://www.finax.eu/ OKI - Osobiste Konto Inwestycyjne', 'Konto', 'OKI - Osobiste Konto Inwestycyjne'),
    ('Handel 24/7 trading bez przerw', 'trading', 'Handel 24/7 trading bez przerw'),
]
for tekst, slowo, oczekiwany in POCZATKI:
    mam = wymogi.cytat(tekst, re.search(slowo, tekst))
    zle += mam != oczekiwany
    print('OK  ' if mam == oczekiwany else 'FAIL', 'a quote starts with the words of the ad |', repr(mam))

menu = 'Szukaj pl menu dostępności wysoki kontrast oferujemy family office dla rodzin i firm w regionie'
mam = doradztwo.sygnaly(menu, {'stan': 'poza_listami', 'podmiot': None, 'panstwo': None, 'lista': None})
zle += mam != []
print('OK  ' if mam == [] else 'FAIL', 'a site menu next to the phrase gives no finding |', [s['kod'] for s in mam])

print(f'{len(PROBY) + len(POCZATKI) + 8 - zle} of {len(PROBY) + len(POCZATKI) + 8} checks passed')
sys.exit(1 if zle else 0)
