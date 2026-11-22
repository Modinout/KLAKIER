# Kolejka zadań dla robotnika: lista Redisa z domenami dla patrolu i druga z linkami wklejonymi w panelu.
import os

LISTA = 'patrol:domeny'
# Wypełniana przez api (api/sprawdzenia.py).
LINKI = 'patrol:linki'


def polaczenie():
    # Import tutaj, żeby testy offline działały bez zainstalowanego redis.
    import redis

    # Robotnik czeka godzinami między zadaniami; domyślny limit gniazda 5 s przerwałby to czekanie.
    return redis.Redis.from_url(os.environ['KOLEJKA_URL'], decode_responses=True, socket_timeout=None)


def dodaj(domena):
    polaczenie().rpush(LISTA, domena)


def pobierz(tylko_linki=False):
    """Czeka, aż w kolejce pojawi się zadanie, i je pobiera; zwraca nazwę jego listy i zadanie."""
    # BLPOP przegląda listy w podanej kolejności, więc link, na który czeka analityk, idzie przed następną domeną.
    return polaczenie().blpop([LINKI] if tylko_linki else [LINKI, LISTA])
