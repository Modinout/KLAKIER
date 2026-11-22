# Wysyła reklamy z pliku JSONL (jedna reklama na linię, pola jak w KONTRAKT.md) do api.
import json
import os
import sys

import httpx

API_URL = os.environ['API_URL']


def wyslij(sciezka):
    dodane = pominiete = 0
    with open(sciezka, encoding='utf-8') as plik:
        for linia in plik:
            odpowiedz = httpx.post(f'{API_URL}/reklamy', json=json.loads(linia), timeout=60)
            if odpowiedz.status_code == 409:
                pominiete += 1
                continue
            odpowiedz.raise_for_status()
            dodane += 1
    print(f'dodane: {dodane}, pominiete (juz w bazie): {pominiete}')


if __name__ == '__main__':
    wyslij(sys.argv[1])
