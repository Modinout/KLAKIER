# Kontrakt danych

Jedno miejsce, w którym usługi uzgadniają kształt danych. Zmiana tutaj oznacza zmianę w `baza/schemat.sql` i `api/schematy.py`.

## Reklama od zbieracza

`POST /reklamy`

| Pole | Typ | Opis |
| --- | --- | --- |
| `zrodlo` | tekst | skąd pochodzi rekord, np. `plik`, `google_ads` |
| `id_zrodla` | tekst | identyfikator reklamy w źródle; para `zrodlo` + `id_zrodla` jest unikalna |
| `platforma` | tekst | gdzie reklamę wyświetlono, np. `facebook`, `google` |
| `url` | tekst lub null | adres, do którego prowadzi reklama |
| `reklamodawca` | tekst lub null | nazwa podana w reklamie |
| `tekst` | tekst | treść reklamy |
| `zebrano` | data i czas (ISO 8601) | kiedy zbieracz ją zapisał |

Odpowiedź: `201` i pełna reklama, albo `409`, gdy taka reklama już jest w bazie.

## Reklama w bazie i w panelu

Pola jak wyżej oraz:

| Pole | Typ | Opis |
| --- | --- | --- |
| `id` | liczba | numer w bazie |
| `dodano` | data i czas | kiedy trafiła do bazy |
| `werdykt` | `ok`, `do_sprawdzenia`, `oszustwo` | najbardziej prawdopodobna klasa według modelu |
| `ryzyko` | liczba 0-1 | prawdopodobieństwo oszustwa |
| `pewny` | prawda / fałsz | fałsz oznacza, że ocenić powinien człowiek |
| `sygnaly` | lista | co znalazły moduły; każdy sygnał ma `modul`, `kod`, `opis`, `podstawa` |
| `status` | `nowa`, `w_toku`, `zamknieta` | etap pracy analityka |

## Adresy api

| Adres | Co robi |
| --- | --- |
| `POST /reklamy` | dodaje reklamę i od razu ją ocenia |
| `GET /reklamy?werdykt=&status=&min_ryzyko=` | lista od największego ryzyka; każdy filtr można pominąć |
| `GET /reklamy/{id}` | jedna reklama |
| `PATCH /reklamy/{id}` | zmiana statusu, treść: `{"status": "w_toku"}` |
| `GET /progi` | dane dla suwaka progu: ile oszustw łapie dany próg i ile daje fałszywych alarmów |

Panel woła te same adresy z przedrostkiem `/api`.

## Adresy ai

| Adres | Co robi |
| --- | --- |
| `POST /ocen` | przyjmuje `tekst`, `reklamodawca`, `url`; zwraca `werdykt`, `ryzyko`, `pewny`, `sygnaly` |
| `GET /progi` | tabela progów z `ai/progi.csv` |
