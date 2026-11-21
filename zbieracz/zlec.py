# Puts domains into the patrol queue.
# Usage: python zlec.py [domena ...]; with no domains it queues the whole KNF warning list.
import sys

import kolejka
import patrol


def zlec(domeny):
    domeny = domeny or list(patrol.wczytaj_ostrzezenia())
    for domena in domeny:
        kolejka.dodaj(domena)
    print(f'Zlecono sprawdzenie domen: {len(domeny)}')


if __name__ == '__main__':
    zlec(sys.argv[1:])
