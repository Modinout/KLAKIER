# The link checker runs inside the stack, so a pasted link could otherwise reach the stack's own services
# or the local network.
import ipaddress
import socket
from urllib.parse import urlsplit


def wewnetrzny(host):
    """True when the host is, or resolves to, an address outside the public internet."""
    try:
        adresy = {informacja[4][0] for informacja in socket.getaddrinfo(host, None)}
    except (socket.gaierror, UnicodeError):
        return False
    return any(not ipaddress.ip_address(adres.split('%')[0]).is_global for adres in adresy)


def prowadzi_do_wewnetrznego(adresy):
    """True when any of the addresses points into the local network."""
    return any(wewnetrzny(host) for host in {urlsplit(adres).hostname for adres in adresy} if host)
