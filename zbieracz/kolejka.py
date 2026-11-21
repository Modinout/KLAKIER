# Task queue for the patrol: one Redis list of domains to check.
import os

LISTA = 'patrol:domeny'


def polaczenie():
    # Imported here so the offline tests run without redis installed.
    import redis

    # The worker waits for hours between tasks; the default 5 s socket timeout would cut that wait.
    return redis.Redis.from_url(os.environ['KOLEJKA_URL'], decode_responses=True, socket_timeout=None)


def dodaj(domena):
    polaczenie().rpush(LISTA, domena)


def pobierz():
    """Waits until a domain is in the queue and takes it."""
    return polaczenie().blpop(LISTA)[1]
