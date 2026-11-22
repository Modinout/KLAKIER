# Sprawdza przez RDAP, kiedy zarejestrowano domeny docelowe reklam, i wysyła każdą datę do api, które zamienia młodą
# domenę reklamy inwestycyjnej w ustalenie przy każdym odczycie.
# Użycie: python wiek_domen.py [domena ...]; bez domen bierze domeny docelowe wszystkich reklam.
import os
import sys
import time

import httpx

# Etykiety drugiego poziomu pod kodem kraju, które nie nazywają żadnej marki, jak w co.uk czy com.pl.
OGOLNE = {'co', 'com', 'net', 'org', 'gov', 'edu', 'ac'}
# rdap.org to darmowa usługa współdzielona; jedno żądanie na sekundę utrzymuje uprzejmy przebieg.
ODSTEP_S = 1


def domeny_reklam():
    reklamy = httpx.get(f"{os.environ['API_URL']}/reklamy", timeout=120).raise_for_status().json()
    return sorted({reklama['domena'] for reklama in reklamy if reklama['domena']})


def w_rejestrze(domena):
    """Nazwa, którą trzyma rejestr, jak pekao.com.pl dla www.pekao.com.pl."""
    czesci = domena.lower().split('.')
    ile = 3 if len(czesci) > 2 and len(czesci[-1]) == 2 and czesci[-2] in OGOLNE else 2
    return '.'.join(czesci[-ile:])


def data_rejestracji(klient, domena):
    """Dzień rejestracji według RDAP albo None, gdy rejestr go nie podaje."""
    time.sleep(ODSTEP_S)
    odpowiedz = klient.get(f'https://rdap.org/domain/{domena}', follow_redirects=True, timeout=30).raise_for_status()
    for zdarzenie in odpowiedz.json().get('events', []):
        if zdarzenie.get('eventAction') == 'registration':
            return zdarzenie['eventDate'][:10]
    return None


def sprawdz_wszystkie(domeny):
    daty = {}
    zapisane = bledy = 0
    with httpx.Client() as klient:
        for domena in domeny:
            nazwa = w_rejestrze(domena)
            try:
                if nazwa not in daty:
                    daty[nazwa] = data_rejestracji(klient, nazwa)
                if daty[nazwa] is None:
                    raise ValueError('RDAP nie podaje daty rejestracji')
                httpx.put(f"{os.environ['API_URL']}/domeny/{domena}", json={'zarejestrowano': daty[nazwa]},
                          timeout=30).raise_for_status()
                zapisane += 1
                print(f'{domena}: zarejestrowana {daty[nazwa]}', flush=True)
            except (httpx.HTTPError, ValueError) as blad:
                bledy += 1
                print(f'{domena}: pomijam, {" ".join(str(blad).split())[:150]}', flush=True)
    print(f'Podsumowanie: domen {len(domeny)}, z datą {zapisane}, błędów {bledy}')


if __name__ == '__main__':
    sprawdz_wszystkie(sys.argv[1:] or domeny_reklam())
