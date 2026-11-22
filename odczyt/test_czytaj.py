# Test dymny czytnika. Uruchom: docker compose run --rm odczyt python test_czytaj.py
import io
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
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

olbrzym = io.BytesIO()
Image.new('L', (6000, 6000)).save(olbrzym, 'PNG')
try:
    czytaj(olbrzym.getvalue())
    sprawdz(False, 'a 36 MP image raises ValueError before decoding')
except ValueError:
    sprawdz(True, 'a 36 MP image raises ValueError before decoding,', len(olbrzym.getvalue()), 'bytes')

import time
from sluchaj import sluchaj

with open('probka_mowa.mp3', 'rb') as plik:
    start = time.perf_counter()
    mowa = sluchaj(plik.read())
print(mowa, f'({time.perf_counter() - start:.1f} s)')
for slowo in ('invest', 'tesla', 'month', 'register'):
    sprawdz(slowo in mowa.lower(), 'probka_mowa.mp3 contains', slowo)
try:
    sluchaj(b'to nie nagranie')
    sprawdz(False, 'bytes that are not a recording raise ValueError')
except ValueError:
    sprawdz(True, 'bytes that are not a recording raise ValueError')

print('SMOKE', liczba - zle, 'of', liczba, 'passed')
sys.exit(1 if zle else 0)
