# Sprawdzenie wektorów reklam. Uruchom: docker compose run --rm ai python test_osadzenia.py
import json
import subprocess
import sys
sys.stdout.reconfigure(encoding='utf-8')
from osadzenia import WYMIARY, osadz

REKLAMA = 'Zainwestuj 900 zł i zarabiaj 20 000 zł miesięcznie. Program rządowy dla każdego Polaka, zysk gwarantowany.'
ZMIENIONA = 'Zainwestuj 1000 zł i zarabiaj 25 000 zł miesięcznie. Program rządowy dla każdego Polaka, zysk pewny.'
INNA = 'Konto maklerskie bez opłat za prowadzenie. Inwestowanie wiąże się z ryzykiem utraty kapitału.'


def cos(a, b):
    return sum(x * y for x, y in zip(a, b))


wektor = osadz(REKLAMA)
bliska, daleka = cos(wektor, osadz(ZMIENIONA)), cos(wektor, osadz(INNA))
# Drugi interpreter musi umieścić ten sam tekst w tym samym punkcie, inaczej zapisane wektory się zdezaktualizują.
drugi = json.loads(subprocess.run(
    [sys.executable, '-c', 'import json, sys, osadzenia; print(json.dumps(osadzenia.osadz(sys.argv[1])))', REKLAMA],
    capture_output=True, text=True, encoding='utf-8', check=True,
).stdout)

PROBY = [
    (f'{WYMIARY} numbers', len(wektor) == WYMIARY),
    ('unit length', abs(cos(wektor, wektor) - 1) < 0.01),
    (f'the same ad with a few words changed is close ({bliska:.3f})', bliska > 0.9),
    (f'an unrelated ad is far ({daleka:.3f})', daleka < 0.6),
    ('the same vector in a fresh interpreter', drugi == wektor),
    ('no text, no vector', osadz('') is None and osadz('   ') is None),
]
zle = 0
for nazwa, dobrze in PROBY:
    zle += not dobrze
    print('OK  ' if dobrze else 'FAIL', nazwa)
print(f'OSADZENIA {len(PROBY) - zle} of {len(PROBY)} passed')
sys.exit(1 if zle else 0)
