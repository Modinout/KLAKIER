# KLAKIER

Kontrola Linków, Afiliacji, Kampanii I Ekspertów Rynku.

Narzędzie dla analityka nadzoru finansowego. Zbiera reklamy inwestycyjne, ocenia ryzyko oszustwa i pokazuje je w panelu od najbardziej podejrzanych.

## Uruchomienie

Potrzebny jest Docker z Compose.

```
cp .env.example .env
docker compose up -d --build
docker compose --profile zbieracz run --rm zbieracz
```

W pliku `.env` ustaw własne hasło bazy. Trzecia komenda wczytuje przykładowe reklamy z `zbieracz/przyklad.jsonl`.

Zmienne `DUZY_MODEL_URL`, `DUZY_MODEL_NAZWA` i `DUZY_MODEL_KLUCZ` w `.env` są opcjonalne: wskazują duży model, który daje drugą ocenę niepewnych reklam i pisze przykłady dla nowych rodzajów oszustw. Bez nich te dwie funkcje są wyłączone.

- Panel: http://localhost:8080
- Opis API w przeglądarce: http://localhost:8000/docs
- Czysty start bazy: `docker compose down -v` (kasuje też to, czego model nauczył się od analityka, i dodane rodzaje oszustw)

## Patrol listy ostrzeżeń

```
docker compose --profile patrol up -d --no-deps kolejka robotnik harmonogram
docker compose --profile patrol run --rm --no-deps patrol python patrol.py <domena>
```

Pierwsza komenda włącza kolejkę zadań, robotnika i harmonogram, który co noc zleca sprawdzenie każdej domeny z listy ostrzeżeń KNF. Druga sprawdza jedną domenę od ręki.

Zmienne `ZBIERACZ_USER_AGENTS` i `ZBIERACZ_PROXY` w `.env` są opcjonalne: listy po przecinku, z których każde kolejne zadanie bierze następną wartość. Puste oznaczają własny User-Agent przeglądarki i brak proxy. Strona, która odmawia, nie jest odpytywana ponownie.

## Usługi

| Katalog | Co robi |
| --- | --- |
| `zbieracz` | wysyła reklamy z pliku JSONL do `api`; patrol sprawdza domeny z listy ostrzeżeń KNF (reklamy Google na Polskę, druga domena tej samej strony, lista CERT) |
| `api` | przyjmuje reklamy, prosi `ai` o ocenę, zapisuje je w bazie i podaje panelowi |
| `ai` | ocenia tekst reklamy małym klasyfikatorem na CPU (opis i ograniczenia: `ai/KARTA_MODELU.md`); uczy się z werdyktów analityka; stan nauki trzyma w wolumenie `stan_ai`; dodaje ustalenia trzech modułów: M1 płatnik a rejestry KNF (`rejestr.py`), M2 informacja o ryzyku (`wymogi.py`), M3 doradztwo bez zezwolenia (`doradztwo.py`) |
| `odczyt` | odczytuje tekst z obrazu reklamy (PP-OCR na CPU); modele są w obrazie Dockera |
| `baza` | Postgres, jedna tabela `reklamy` (`baza/schemat.sql`) |
| `front` | panel: kolejka spraw z filtrami (data, źródło, status, ryzyko, moduł) i wykresem trendu, karta sprawy z obrazem reklamy, ustaleniami i decyzją, alerty na żywo, kalibracja progu |

Pola reklamy i adresy API opisuje `KONTRAKT.md`.

## Testy

```
docker compose run --rm ai python test_przewidz.py
docker compose run --rm ai python test_rejestr.py
docker compose run --rm ai python test_wymogi.py
docker compose run --rm ai python test_osadzenia.py
uv run --with pytest --with httpx --with websockets pytest testy
docker compose run --rm odczyt python test_czytaj.py
```

Test z katalogu `testy` wymaga działających usług. Reklamy testowe, które dodaje do bazy, usuwa na końcu. Model zostawia taki, jaki był.

## Gdzie co dopisać

- Nowe źródło reklam: nowy plik w `zbieracz/`, który wysyła rekordy na `POST /reklamy`.
- Nowy sygnał: własny plik w `ai/` na wzór `wymogi.py`, z testem, dołączony do listy `sygnaly` w `/ocen` (`ai/main.py`).
- Nowe pole reklamy: `baza/schemat.sql`, `api/schematy.py`, `KONTRAKT.md`.
