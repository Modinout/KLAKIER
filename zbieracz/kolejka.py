# Kolejka zadań dla robotnika: listy Redisa z domenami dla patrolu, z linkami wklejonymi w panelu i z frazami do wyszukania.
import json
import os

LISTA = 'patrol:domeny'
# Wypełniana przez api (api/sprawdzenia.py).
LINKI = 'patrol:linki'
# Frazy do wyszukania w bibliotece reklam TikToka, zlecane w panelu (api/patrol.py).
FRAZY = 'patrol:frazy'
OSTATNIE = 'patrol:ostatnie'


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
    return polaczenie().blpop([LINKI, FRAZY] if tylko_linki else [LINKI, FRAZY, LISTA])


def zapisz_wyszukiwanie(id, stan):
    """Zapisuje stan wyszukiwania frazy; zakończone zostaje też jako ostatnie."""
    zapis = json.dumps(stan)
    kolejka = polaczenie()
    kolejka.set(f'patrol:wyszukiwanie:{id}', zapis)
    if stan['stan'] != 'w_toku':
        kolejka.set(OSTATNIE, zapis)
