# User-Agenty i proxy ustawione przez operatora, wydawane po kolei: każdy nowy kontekst przeglądarki bierze następne.
import os

uzyte = {}


def kolejny(nazwa):
    """Następna wartość listy rozdzielonej '|' ze zmiennej środowiskowej albo None, gdy jest pusta."""
    wartosci = [wartosc.strip() for wartosc in os.environ.get(nazwa, '').split('|') if wartosc.strip()]
    if not wartosci:
        return None
    numer = uzyte.get(nazwa, 0)
    uzyte[nazwa] = numer + 1
    return wartosci[numer % len(wartosci)]


def ustawienia():
    """User-Agent i proxy dla nowego kontekstu przeglądarki; None zostawia własne ustawienia przeglądarki."""
    proxy = kolejny('ZBIERACZ_PROXY')
    return {'user_agent': kolejny('ZBIERACZ_USER_AGENTS'), 'proxy': {'server': proxy} if proxy else None}
