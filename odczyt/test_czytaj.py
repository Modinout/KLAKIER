# Smoke test of the reader. Run: docker compose run --rm odczyt python test_czytaj.py
import sys
sys.stdout.reconfigure(encoding='utf-8')
from czytaj import czytaj

liczba = zle = 0


def sprawdz(dobrze, *opis):
    global liczba, zle
    liczba += 1
    zle += not dobrze
    print('OK  ' if dobrze else 'FAIL', *opis)


with open('probka.png', 'rb') as plik:
    tekst = czytaj(plik.read())
print(tekst.replace('\n', ' / '))
for slowo in ('zainwestuj', '900', 'miesięcznie', 'gwarantowany'):
    sprawdz(slowo in tekst.lower(), 'probka.png contains', slowo)

try:
    czytaj(b'to nie obraz')
    sprawdz(False, 'bytes that are not an image raise ValueError')
except ValueError:
    sprawdz(True, 'bytes that are not an image raise ValueError')

print('SMOKE', liczba - zle, 'of', liczba, 'passed')
sys.exit(1 if zle else 0)
