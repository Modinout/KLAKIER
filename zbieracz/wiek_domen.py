# Looks up by RDAP when the landing domains of the ads were registered and sends each date to the api, which turns a
# young domain of an investment ad into a finding on every read.
# Usage: python wiek_domen.py [domena ...]; with no domains it takes the landing domains of all ads.
import os
import sys
import time

import httpx

# Second-level labels under a country code that name no brand, as in co.uk or com.pl.
OGOLNE = {'co', 'com', 'net', 'org', 'gov', 'edu', 'ac'}
# rdap.org is a free shared service; one request a second keeps the run polite.
ODSTEP_S = 1


def domeny_reklam():
    reklamy = httpx.get(f"{os.environ['API_URL']}/reklamy", timeout=120).raise_for_status().json()
    return sorted({reklama['domena'] for reklama in reklamy if reklama['domena']})


def w_rejestrze(domena):
    """The name a registry holds, as in pekao.com.pl for www.pekao.com.pl."""
    czesci = domena.lower().split('.')
    ile = 3 if len(czesci) > 2 and len(czesci[-1]) == 2 and czesci[-2] in OGOLNE else 2
    return '.'.join(czesci[-ile:])


def data_rejestracji(klient, domena):
    """Day of registration by RDAP, or None when the registry does not give it."""
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
