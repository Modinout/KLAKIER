# Task queue for the robotnik: a Redis list of domains for the patrol and one of links pasted in the panel.
import os

LISTA = 'patrol:domeny'
# Filled by the api (api/sprawdzenia.py).
LINKI = 'patrol:linki'


def polaczenie():
    # Imported here so the offline tests run without redis installed.
    import redis

    # The worker waits for hours between tasks; the default 5 s socket timeout would cut that wait.
    return redis.Redis.from_url(os.environ['KOLEJKA_URL'], decode_responses=True, socket_timeout=None)


def dodaj(domena):
    polaczenie().rpush(LISTA, domena)


def pobierz(tylko_linki=False):
    """Waits until a task is in the queue and takes it; returns the name of its list and the task."""
    # BLPOP looks at the lists in the order given, so an analyst waiting for a link goes before the next domain.
    return polaczenie().blpop([LINKI] if tylko_linki else [LINKI, LISTA])
