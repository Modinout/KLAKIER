# KLAKIER

Kontrola Linków, Afiliacji, Kampanii I Ekspertów Rynku.

Narzędzie dla analityka nadzoru finansowego. Zbiera reklamy inwestycyjne, ocenia ryzyko oszustwa i pokazuje je w panelu od najbardziej podejrzanych.

## Uruchomienie

Potrzebny jest Docker z Compose.

```
cp .env.example .env
docker compose up -d --build
docker compose --profile zbieracz run --rm zbieracz python z_pliku.py pokaz.jsonl
```

W pliku `.env` ustaw własne hasło bazy. Trzecia komenda wczytuje 144 prawdziwe reklamy z `zbieracz/pokaz.jsonl`, w tym 32 oszustwa z ostrzeżeń CSIRT KNF.

Zmienne `DUZY_MODEL_URL`, `DUZY_MODEL_NAZWA` i `DUZY_MODEL_KLUCZ` w `.env` są opcjonalne: wskazują duży model, który daje drugą ocenę niepewnych reklam i pisze przykłady dla nowych rodzajów oszustw. Bez nich te dwie funkcje są wyłączone.

- Panel: http://localhost:8080
- Opis API w przeglądarce: http://localhost:8000/docs
- Czysty start bazy: `docker compose down -v` (kasuje też to, czego model nauczył się od analityka, i dodane rodzaje oszustw)

## Patrol listy ostrzeżeń

```
docker compose --profile patrol up -d --no-deps kolejka robotnik harmonogram
docker compose --profile patrol run --rm --no-deps patrol python patrol.py <domena>
docker compose --profile patrol run --rm --no-deps patrol python tiktok.py [fraza ...]
docker compose --profile patrol run --rm --no-deps patrol python strony_docelowe.py [domena ...]
docker compose --profile patrol run --rm --no-deps patrol python wiek_domen.py [domena ...]
```

Pierwsza komenda włącza kolejkę zadań, robotnika i harmonogram, który co noc uruchamia patrol domen z listy ostrzeżeń KNF, wyszukiwanie fraz w bibliotece reklam TikToka, pomiar ostrzeżenia o ryzyku na stronach docelowych, a gdy w `.env` jest `META_TOKEN`, także zbieranie reklam Mety przez oficjalne API. Druga sprawdza jedną domenę od ręki. Trzecia zbiera reklamy z publicznej biblioteki reklam TikToka dla Polski; bez podanych fraz szuka pięciu wbudowanych fraz inwestycyjnych, najwyżej 10 reklam na frazę. Czwarta mierzy ostrzeżenie o ryzyku na stronach głównych domen, do których prowadzą reklamy firm z rejestru KNF, na komputerze i na telefonie, i zapisuje pomiar w api; bez podanych domen bierze wszystkie takie domeny z bazy. Piąta sprawdza w RDAP, kiedy zarejestrowano domeny docelowe reklam, najwyżej jednym zapytaniem na sekundę, i zapisuje datę w api; bez podanych domen bierze wszystkie domeny docelowe z bazy.

Reklamy z Mety (Facebook, Instagram, Messenger) zbiera `meta_api.py` przez oficjalne API Biblioteki reklam Mety. Harmonogram uruchamia go co noc: szuka tych samych pięciu fraz inwestycyjnych co zbieracz TikToka w reklamach, które dotarły do Polski w ostatnich dwóch dniach, i wysyła nowe do bazy. API zwraca reklamy pokazane w Unii Europejskiej na każdy temat, więc obejmuje też reklamy inwestycyjne. Potrzebny jest token dostępu wpisany w `.env` jako `META_TOKEN`; jak go uzyskać, opisuje https://www.facebook.com/ads/library/api/. Bez tokenu `meta_api.py` tylko zapisuje w logu, że pomija Metę. Ręczne uruchomienie: `docker compose --profile patrol run --rm --no-deps -e META_TOKEN=<token> patrol python meta_api.py`.

W tym repozytorium tokenu nie ma, dlatego reklamy Mety w danych pokazowych pochodzą z ręcznego importu: analityk zapisuje stronę wyników Biblioteki reklam w przeglądarce, a `python meta.py strona.html` wczytuje z niej reklamy do bazy. Automatycznych wizyt na stronie biblioteki nie robimy, bo Meta ich zabrania.

Zmienne `ZBIERACZ_USER_AGENTS` i `ZBIERACZ_PROXY` w `.env` są opcjonalne: listy po przecinku, z których każde kolejne zadanie bierze następną wartość. Puste oznaczają własny User-Agent przeglądarki i brak proxy. Strona, która odmawia, nie jest odpytywana ponownie.

## Źródła reklam: dziś i docelowo

Dziś system bierze reklamy z Centrum przejrzystości reklam Google, z publicznej biblioteki reklam TikToka, z opisów filmów na YouTube i z ręcznie zapisanych stron Biblioteki reklam Mety. Domeny docelowe sprawdza na liście ostrzeżeń publicznych KNF, w ostrzeżeniach CSIRT KNF i na liście ostrzeżeń CERT Polska.

Docelowo reklamy powinny przychodzić z oficjalnych interfejsów, które duże platformy muszą udostępniać na mocy aktu o usługach cyfrowych (DSA):

- Meta: API Biblioteki reklam; `meta_api.py` jest gotowy, brakuje tokenu.
- TikTok: Commercial Content API zamiast strony biblioteki; dostęp dostaje się po zatwierdzeniu wniosku przez TikToka.
- Google: zbiór Ads Transparency Center w BigQuery (Europejski Obszar Gospodarczy i Turcja), z osobną tabelą reklam usuniętych przez Google, z miejscem i powodem usunięcia.
- Microsoft: publiczne API biblioteki reklam z wyszukiwarki Bing, bez logowania.
- X, LinkedIn, Snapchat, Pinterest: biblioteki reklam z obowiązku DSA, do sprawdzenia.

Czego brakuje:

- tokenu do API Mety i dostępu do API TikToka;
- pola na płatnika i beneficjenta reklamy, które API Mety podaje dla reklam pokazanych w Unii;
- źródła reklam na portalach informacyjnych, np. podrobionych artykułów ze znanymi osobami w ramkach z polecanymi tekstami: takie reklamy nie mają publicznej biblioteki.

## Usługi

| Katalog | Co robi |
| --- | --- |
| `zbieracz` | wysyła reklamy z pliku JSONL do `api`; patrol sprawdza domeny z listy ostrzeżeń KNF (reklamy Google na Polskę, druga domena tej samej strony, lista CERT) |
| `api` | przyjmuje reklamy, prosi `ai` o ocenę, zapisuje je w bazie i podaje panelowi; przy każdym odczycie dokłada ustalenia o domenie docelowej: płatnicy domeny i ostrzeżenie o ryzyku na stronie |
| `ai` | ocenia tekst reklamy małym klasyfikatorem KAPSEL na CPU (opis i ograniczenia: `ai/KARTA_MODELU.md`); uczy się z werdyktów analityka; stan nauki trzyma w wolumenie `stan_ai`; dodaje ustalenia trzech modułów: M1 płatnik a rejestry KNF (`rejestr.py`), M2 informacja o ryzyku (`wymogi.py`), M3 doradztwo bez zezwolenia (`doradztwo.py`) |
| `odczyt` | odczytuje tekst z obrazu reklamy (PP-OCR na CPU); modele są w obrazie Dockera |
| `baza` | Postgres, tabele `reklamy`, `obrazy_reklam` i `strony` (`baza/schemat.sql`) |
| `front` | panel: kolejka spraw z filtrami (data, źródło, status, ryzyko, moduł) i wykresem trendu, karta sprawy z obrazem reklamy, ustaleniami i decyzją, notatka i historia zmian sprawy, dowody z paczką do pobrania, powiązane sprawy, gotowe zgłoszenie sprawy w toku do skopiowania albo pobrania, sprawdzenie wklejonego linku, raport CSV z bieżącego widoku i filtrów, alerty na żywo, kalibracja progu i zastosowanie go w kolejce |

Pola reklamy i adresy API opisuje `KONTRAKT.md`.

## Testy

```
docker compose run --rm ai python test_przewidz.py
docker compose run --rm ai python test_main.py
docker compose run --rm ai python test_rejestr.py
docker compose run --rm ai python test_wymogi.py
docker compose run --rm ai python test_osadzenia.py
docker compose run --rm ai python test_temat.py
docker compose run --rm ai python test_polecenia.py
uv run --with pytest --with httpx --with websockets pytest testy
docker compose run --rm odczyt python test_czytaj.py
docker compose --profile patrol run --rm --no-deps patrol python -m pytest test_pomiar_ostrzezenia.py test_patrol.py
```

Test z katalogu `testy` wymaga działających usług. Reklamy testowe, które dodaje do bazy, usuwa na końcu. Model zostawia taki, jaki był.

GitHub Actions (`.github/workflows/sprawdzenie.yml`) przy każdym pushu i pull requeście buduje panel, uruchamia testy `ai` i `zbieracz`, które nie potrzebują działających usług, i skanuje zależności (`npm audit`, `pip-audit`). Dependabot (`.github/dependabot.yml`) co tydzień proponuje aktualizacje bibliotek, obrazów Dockera i akcji.

## Gdzie co dopisać

- Nowe źródło reklam: nowy plik w `zbieracz/`, który wysyła rekordy na `POST /reklamy`.
- Nowy sygnał: własny plik w `ai/` na wzór `wymogi.py`, z testem, dołączony do listy `sygnaly` w `/ocen` (`ai/main.py`).
- Nowe pole reklamy: `baza/schemat.sql`, `api/schematy.py`, `KONTRAKT.md`.
