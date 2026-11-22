# Lista ostrzeżeń CERT Polska: domeny, które blokują polscy operatorzy.
import httpx

ADRES = 'https://hole.cert.pl/domains/v2/domains.json'

domeny = set()


def wczytaj():
    odpowiedz = httpx.get(ADRES, timeout=120)
    odpowiedz.raise_for_status()
    # Wpisy z datą usunięcia zdjęto z listy i nie są już blokowane.
    domeny.update(wpis['DomainAddress'].lower() for wpis in odpowiedz.json() if not wpis['DeleteDate'])


def na_liscie(host):
    czesci = host.lower().split('.')
    return any('.'.join(czesci[i:]) in domeny for i in range(len(czesci)))
