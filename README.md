# KLAKIER

Kontrola Linków, Afiliacji, Kampanii I Ekspertów Rynku.

Narzędzie dla analityka nadzoru finansowego. Zbiera reklamy inwestycyjne, ocenia ryzyko oszustwa i pokazuje je w panelu od najbardziej podejrzanych.

Stan: szkielet. Działa jedna pełna ścieżka: plik z reklamami, ocena, baza, panel.

## Uruchomienie

Potrzebny jest Docker z Compose.

```
cp .env.example .env
docker compose up -d --build
docker compose --profile zbieracz run --rm zbieracz
```

W pliku `.env` ustaw własne hasło bazy. Trzecia komenda wczytuje przykładowe reklamy z `zbieracz/przyklad.jsonl`.

- Panel: http://localhost:8080
- Opis API w przeglądarce: http://localhost:8000/docs
- Czysty start bazy: `docker compose down -v`

## Usługi

| Katalog | Co robi |
| --- | --- |
| `zbieracz` | wysyła reklamy z pliku JSONL do `api` |
| `api` | przyjmuje reklamy, prosi `ai` o ocenę, zapisuje je w bazie i podaje panelowi |
| `ai` | ocenia tekst reklamy małym klasyfikatorem na CPU (opis i ograniczenia: `ai/KARTA_MODELU.md`) |
| `baza` | Postgres, jedna tabela `reklamy` (`baza/schemat.sql`) |
| `front` | panel: lista, filtry, próg ryzyka, karta sprawy |

Pola reklamy i adresy API opisuje `KONTRAKT.md`.

## Testy

```
docker compose run --rm ai python test_przewidz.py
uv run --with pytest --with httpx pytest testy
```

Drugi test wymaga działających usług i dodaje do bazy jedną reklamę testową.

## Gdzie co dopisać

- Nowe źródło reklam: nowy plik w `zbieracz/`, który wysyła rekordy na `POST /reklamy`.
- Nowy sygnał (rejestry KNF, zasady UKNF, doradztwo bez licencji): `ai/main.py`, lista `sygnaly` w odpowiedzi `/ocen`.
- Nowe pole reklamy: `baza/schemat.sql`, `api/schematy.py`, `KONTRAKT.md`.
