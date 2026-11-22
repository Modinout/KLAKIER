# Wkłada domeny do kolejki patrolu.
# Użycie: python zlec.py [domena ...]; bez domen kolejkuje całą listę ostrzeżeń KNF.
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
