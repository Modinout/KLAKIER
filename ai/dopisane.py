# Reklamy dopisane w trakcie działania: przykłady analityków.
import json
import pathlib

PLIK = pathlib.Path(__file__).parent / 'stan' / 'dopisane.jsonl'


def czytaj():
    if not PLIK.exists():
        return []
    with PLIK.open(encoding='utf-8') as plik:
        return [json.loads(linia) for linia in plik]


def zapisz(wiersze):
    PLIK.parent.mkdir(exist_ok=True)
    with PLIK.open('w', encoding='utf-8', newline='\n') as plik:
        for wiersz in wiersze:
            plik.write(json.dumps(wiersz, ensure_ascii=False) + '\n')
