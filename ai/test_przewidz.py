# Smoke test of the classifier. Run: docker compose run --rm ai python test_przewidz.py
import sys
sys.stdout.reconfigure(encoding='utf-8')
import dopisane
from przewidz import _werdykt, przeucz, przewidz, znane_rodzaje
from tekst import oczysc

assert oczysc('Motywacja\nSponsorowane\nNVIDIA obiecuje\nDowiedz się więcej\nIdentyfikator: 123') == 'NVIDIA obiecuje'
assert oczysc('Sponsored\nPlus500\nwww.plus500.com/\nLearn More') == 'Plus500\nwww.plus500.com/'
PROBY = [
    ('oszustwo', 'Zainwestuj 900 zł z Orlen i zarabiaj 20 000 zł miesięcznie! Gwarantowany dochód dla każdego Polaka. Zarejestruj się, liczba miejsc ograniczona'),
    ('oszustwo', 'Motywacja\nSponsorowane\nPGE daje 100 uczestnikom dostęp do oprogramowania, które pozwala zarobić 3 500 Euro każdego dnia!\nDowiedz się więcej'),
    ('nie', 'Inwestuj w akcje i ETF-y bez prowizji do 100 tys. euro obrotu miesięcznie. Inwestowanie wiąże się z ryzykiem.\nLearn More'),
    ('nie', 'Otwórz IKE lub IKZE w naszym banku i odkładaj na emeryturę. Inwestowanie wiąże się z ryzykiem utraty części lub całości środków.'),
    ('nie', 'Nowa kolekcja zimowa już w sklepie. Kurtki i buty do 40% taniej, darmowa dostawa od 200 zł. Tylko do niedzieli!'),
    ('nie', ''),
]
RODZAJE = [
    ('obietnica gwarantowanego zysku', 'Zainwestuj 900 zł i zarabiaj 20 000 zł miesięcznie, zysk gwarantowany!'),
    ('zamknięta grupa z sygnałami', 'Dołącz do naszej zamkniętej grupy na Telegramie. Codziennie sygnały, 95 % skuteczności, pierwszy tydzień za darmo.'),
    ('odzyskiwanie straconych pieniędzy', 'Straciłeś pieniądze u fałszywego brokera? Odzyskamy Twoje środki w 14 dni. Bezpłatna konsultacja.'),
]
liczba = zle = 0


def sprawdz(dobrze, *opis):
    global liczba, zle
    liczba += 1
    zle += not dobrze
    print('OK  ' if dobrze else 'FAIL', *opis)


rodzaje = znane_rodzaje()
for oczek, tekst in PROBY:
    w = przewidz(tekst)
    sprawdz((w['werdykt'] == 'oszustwo') == (oczek == 'oszustwo') and (bool(tekst) or not w['pewny']),
            'expected', oczek.ljust(8), '| got', w['werdykt'].ljust(14), 'scam', format(w['prawdopodobienstwa']['oszustwo'], '.2f'),
            '| pewny', w['pewny'], '|', tekst.replace('\n', ' / ')[:70])
    # A type the model is unsure of comes back as None, and an ad that is not a scam never gets one.
    dobrze = w['rodzaj'] is None or (oczek == 'oszustwo' and w['rodzaj'] in rodzaje)
    sprawdz(dobrze, 'rodzaj', w['rodzaj'], '|', tekst.replace('\n', ' / ')[:70])

for oczek, tekst in RODZAJE:
    rodzaj = przewidz(tekst)['rodzaj']
    sprawdz(rodzaj == oczek, 'expected rodzaj', oczek, '| got', rodzaj)

tekst = PROBY[0][1]
powody = przewidz(tekst)['powody']
sprawdz(bool(powody) and all(p['slowo'] in tekst for p in powody), 'powody', [(p['slowo'], round(p['waga'], 2)) for p in powody])
sprawdz(przewidz(PROBY[3][1])['powody'] == [], 'low-risk ad -> no powody')
# A reason is a plain word: no punctuation around it, no number, link or form label, each word once.
brudny = 'ZARABIAJ 6 500 zł tygodniowo! Zarabiaj z ORLEN. Gwarantowany dochód. Podaj imię, nazwisko i e-mail: orlen-zysk.pl/start'
slowa = [p['slowo'] for p in przewidz(brudny)['powody']]
male = [s.lower() for s in slowa]
sprawdz(bool(slowa) and all(s.isalpha() and len(s) > 2 for s in slowa) and len(set(male)) == len(male)
        and not {'imię', 'nazwisko'} & set(male), 'plain powody', slowa)

# Styled Unicode letters, look-alike Cyrillic letters and invisible characters must not hide a scam.
pogrubione = ''.join(chr(0x1D41A + ord(z) - 97) if 'a' <= z <= 'z' else z for z in tekst)
for nazwa, wersja in [('math bold letters', pogrubione), ('Cyrillic look-alikes', tekst.translate(str.maketrans('aeopcyx', 'аеорсух'))),
                      ('zero-width spaces', '​'.join(tekst))]:
    w = przewidz(wersja)
    sprawdz(w['werdykt'] == 'oszustwo', 'scam written with', nazwa, '-> got', w['werdykt'], format(w['prawdopodobienstwa']['oszustwo'], '.2f'))

w = przewidz(PROBY[2][1])
sprawdz(w['werdykt'] == 'ok' and w['pewny'], 'ordinary broker ad -> got', w['werdykt'], '| pewny', w['pewny'])
pasma = [_werdykt('reklama', p) for p in (0.1, 0.5, 0.9)] + [_werdykt('', 0.9)]
sprawdz(pasma == ['ok', 'do_sprawdzenia', 'oszustwo', 'do_sprawdzenia'], 'verdict by scam probability, no text last ->', pasma)

# An analyst example must change the verdict after retraining, and removing it must change it back.
sklep = PROBY[4][1]
bylo = dopisane.PLIK.exists()
przed = dopisane.czytaj()
try:
    dopisane.zapisz(przed + [{'tekst': oczysc(sklep), 'werdykt': 'oszustwo', 'rodzaj': None, 'pochodzenie': 'analityk'}])
    przeucz()
    w = przewidz(sklep)
    sprawdz(w['werdykt'] == 'oszustwo', 'shop ad as analyst scam example -> got', w['werdykt'])
    dopisane.zapisz([r for r in dopisane.czytaj() if r['pochodzenie'] != 'analityk'])
    przeucz()
    w = przewidz(sklep)
    sprawdz(w['werdykt'] != 'oszustwo', 'analyst rows removed -> got', w['werdykt'])
finally:
    if bylo:
        dopisane.zapisz(przed)
    else:
        dopisane.PLIK.unlink(missing_ok=True)

print('SMOKE', liczba - zle, 'of', liczba, 'passed')
sys.exit(1 if zle else 0)
