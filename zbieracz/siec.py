# Sprawdzacz linków działa wewnątrz stosu, więc wklejony link mógłby inaczej dotrzeć do własnych usług stosu
# lub do sieci lokalnej.
import ipaddress
import socket
from urllib.parse import urlsplit


def wewnetrzny(host):
    """True, gdy host jest adresem spoza publicznego internetu albo się do takiego rozwiązuje."""
    try:
        adresy = {informacja[4][0] for informacja in socket.getaddrinfo(host, None)}
    except (socket.gaierror, UnicodeError):
        return False
    return any(not ipaddress.ip_address(adres.split('%')[0]).is_global for adres in adresy)


def prowadzi_do_wewnetrznego(adresy):
    """True, gdy którykolwiek z adresów wskazuje do sieci lokalnej."""
    return any(wewnetrzny(host) for host in {urlsplit(adres).hostname for adres in adresy} if host)
