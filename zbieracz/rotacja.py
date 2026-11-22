# User-Agents and proxies set by the operator, handed out in turn: each new browser context takes the next ones.
import os

uzyte = {}


def kolejny(nazwa):
    """Next value of the '|'-separated list in the environment variable, or None when it is empty."""
    wartosci = [wartosc.strip() for wartosc in os.environ.get(nazwa, '').split('|') if wartosc.strip()]
    if not wartosci:
        return None
    numer = uzyte.get(nazwa, 0)
    uzyte[nazwa] = numer + 1
    return wartosci[numer % len(wartosci)]


def ustawienia():
    """User-Agent and proxy for a new browser context; None keeps the browser's own."""
    proxy = kolejny('ZBIERACZ_PROXY')
    return {'user_agent': kolejny('ZBIERACZ_USER_AGENTS'), 'proxy': {'server': proxy} if proxy else None}
