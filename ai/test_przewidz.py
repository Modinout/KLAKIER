# Smoke test of the classifier. Run: docker compose run --rm ai python test_przewidz.py
import sys
sys.stdout.reconfigure(encoding='utf-8')
from przewidz import przewidz
from tekst import oczysc

assert oczysc('Motywacja\nSponsorowane\nNVIDIA obiecuje\nDowiedz się więcej\nIdentyfikator: 123') == 'NVIDIA obiecuje'
assert oczysc('Sponsored\nPlus500\nwww.plus500.com/\nLearn More') == 'Plus500\nwww.plus500.com/'
PROBY = [
    ('oszustwo', 'Zainwestuj 900 zł z Orlen i zarabiaj 20 000 zł miesięcznie! Gwarantowany dochód dla każdego Polaka. Zarejestruj się, liczba miejsc ograniczona'),
    ('oszustwo', 'Motywacja\nSponsorowane\nPGE daje 100 uczestnikom dostęp do oprogramowania, które pozwala zarobić 3 500 Euro każdego dnia!\nDowiedz się więcej'),
    ('nie', 'Inwestuj w akcje i ETF-y bez prowizji do 100 tys. euro obrotu miesięcznie. Inwestowanie wiąże się z ryzykiem.\nLearn More'),
    ('nie', 'Otwórz IKE lub IKZE w naszym banku i odkładaj na emeryturę. Inwestowanie wiąże się z ryzykiem utraty części lub całości środków.'),
    ('nie', ''),
]
zle = 0
for oczek, tekst in PROBY:
    w = przewidz(tekst)
    dobrze = (w['werdykt'] == 'oszustwo') == (oczek == 'oszustwo') and (bool(tekst) or not w['pewny'])
    zle += not dobrze
    print('OK  ' if dobrze else 'FAIL', 'expected', oczek.ljust(8), '| got', w['werdykt'].ljust(14), 'scam', format(w['prawdopodobienstwa']['oszustwo'], '.2f'),
          '| pewny', w['pewny'], '|', tekst.replace('\n', ' / ')[:70])
print('SMOKE', len(PROBY) - zle, 'of', len(PROBY), 'passed')
sys.exit(1 if zle else 0)
