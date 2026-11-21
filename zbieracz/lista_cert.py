# CERT Polska warning list: domains that Polish operators block.
import httpx

ADRES = 'https://hole.cert.pl/domains/v2/domains.json'

domeny = set()


def wczytaj():
    odpowiedz = httpx.get(ADRES, timeout=120)
    odpowiedz.raise_for_status()
    # Entries with a delete date were taken off the list and are no longer blocked.
    domeny.update(wpis['DomainAddress'].lower() for wpis in odpowiedz.json() if not wpis['DeleteDate'])


def na_liscie(host):
    czesci = host.lower().split('.')
    return any('.'.join(czesci[i:]) in domeny for i in range(len(czesci)))
