# KLAKIER

Kontrola Linków, Afiliacji, Kampanii I Ekspertów Rynku.

KLAKIER pomaga analitykowi UKNF znaleźć w reklamach inwestycyjnych trzy rodzaje naruszeń: kto płaci za reklamę usług inwestycyjnych, choć nie ma go w rejestrach KNF ani MiCA (M1), czy reklama firmy z rejestru podaje informacje o ryzyku zgodnie z kryteriami UKNF (M2) i kto oferuje doradztwo inwestycyjne bez zezwolenia KNF (M3). Reklamy zbiera z publicznych bibliotek reklam, a w panelu pokazuje je jako sprawy z cytatem, dowodami i podstawą prawną.

KAPSEL to nasz własny model, który czyta tekst reklamy i ocenia, jak bardzo przypomina fałszywą inwestycję. Działa na zwykłym procesorze laptopa, bez internetu, w około milisekundę na reklamę. Zmierzyliśmy go na reklamach, których nie widział przy nauce: bez żadnego fałszywego alarmu wskazuje 74 z 95 prawdziwych oszustw, a każde z 24 świeżo opublikowanych oszustw trafiło co najmniej do sprawdzenia przez człowieka. Przy podejrzanych reklamach pokazuje słowa, które podniosły ryzyko, i ustawia analitykowi najgroźniejsze reklamy na początku kolejki. Jak powstał i gdzie się myli: `ai/KARTA_MODELU.md`.

## Co sprawdza

### M2: kryteria UKNF dla informacji o ryzyku

Tekst reklamy sprawdzają reguły w `ai/wymogi.py`, tylko dla płatników z rejestrów KNF. Stronę docelową reklamy mierzy przeglądarka (`zbieracz/pomiar_ostrzezenia.js`, `api/ostrzezenie_strony.py`) w widoku komputera (1366 px), tabletu (768 px) i telefonu (390 px). Ustalenia z tekstu podają w podstawie numer kryterium UKNF, ustalenia ze strony powołują się na ESMA i WCAG.

| Kryterium UKNF | Stan | Jak sprawdzamy |
| --- | --- | --- |
| 1 Identyfikacja firmy | jeszcze nie | porównujemy płatnika z rejestrami, nie nazwę firmy w materiale |
| 2 Oznaczenie reklamy | częściowo | tylko opisy filmów z linkiem lub kodem polecającym bez oznaczenia współpracy (`ai/polecenia.py`); reklam na platformach nie sprawdzamy |
| 3 Informacja o ryzyku | jest | `zysk_bez_ryzyka`: informacja o ryzyku w dowolnym miejscu tekstu |
| 4 Rozmiar czcionki ostrzeżenia | jest | strona: czcionka ostrzeżenia wobec przeważającej |
| 5 Ekspozycja i kontrast | częściowo | strona: kontrast według WCAG (4,5:1); zasłaniania przez inne elementy nie sprawdzamy |
| 6 Ukrywanie ryzyka | częściowo | strona: ukryty element liczy się jako niewidoczny; przypisu ani zakładki „Legal” nie oznaczamy |
| 7 Dostępność za jednym kliknięciem | częściowo | strona: ostrzeżenie w zwiniętym elemencie liczy się jako brak; klikania nie testujemy |
| 8 Responsywność | częściowo | komputer, tablet i telefon; przycięcia nie sprawdzamy |
| 9 Zrozumiałość | jeszcze nie | |
| 10 Spójność językowa | jest | `ryzyko_w_innym_jezyku`: polska reklama z ostrzeżeniem tylko po angielsku |
| 11 Porównania produktów | jeszcze nie | |
| 12a Wyniki historyczne: okres i źródło | jest | `wyniki_bez_okresu`, gdy reklama podaje wynik w procentach |
| 12b Wyniki historyczne: opłaty i waluta | jest | `wyniki_bez_oplat_i_waluty` |
| 13 Dominacja wyników historycznych | jeszcze nie | wymaga oceny układu reklamy |
| 14 Ostrzeżenie przy wynikach historycznych | jest | `wyniki_bez_zastrzezenia` |
| 15 Prognozy | jest | `prognoza_bez_zastrzezenia`: prognoza z liczbą |
| 16 Informacja podatkowa | jest | `podatki_bez_zastrzezenia` |
| 17 Aprobata organu nadzoru | jest | `nadzor_jako_argument`: „zatwierdzony”, „rekomendowany” albo „approved” obok KNF, CySEC lub FCA |
| 18 Nadzór jako argument bezpieczeństwa | jest | `nadzor_jako_argument` |

Razem 10 kryteriów jest, 5 częściowo, 4 jeszcze nie. Poza listą: reklama CFD albo forex bez standardowego odsetka rachunków ze stratą (`brak_ostrzezenia_cfd`, ESMA 2018/796, dziś interwencja produktowa KNF). Zakresu zezwolenia firmy, np. na doradztwo, nie sprawdzamy.

### Jak trafne są ustalenia

Baza pokazowa, 1782 materiały:

- M1, płatnik a rejestry: 169 ustaleń (87 razy płaci inny podmiot marki z rejestru, 82 razy płatnika nie ma w rejestrach KNF ani w rejestrze MiCA); 59 przypadków w `ai/test_rejestr.py`.
- M1, polecenia u finfluencerów: 54 ustalenia; 20 losowo wybranych przeczytaliśmy ręcznie i wszystkie to prawdziwe linki albo kody polecające. Nie wiemy, czy oznaczenie współpracy padło w samym filmie, dlatego każde takie ustalenie jest „do sprawdzenia”.
- M2, tekst: 9 ustaleń, wszystkie przeczytane ręcznie: 8 trafnych (4 reklamy CFD bez odsetka rachunków ze stratą, 4 obietnice podatkowe bez zastrzeżenia), 1 słabe.
- M2, strona: 13 ustaleń (10 ostrzeżeń mniejszych od tekstu albo o słabym kontraście, 3 strony CFD bez widocznego ostrzeżenia), zmierzonych w przeglądarce, nieprzeczytanych ręcznie.
- M3, doradztwo: 5 ustaleń, 1 słabe (artykuł z listą grup z sygnałami, a nie oferta).
- KAPSEL: 95 prawdziwych oszustw i 374 uczciwe reklamy inwestycyjne, 5 podziałów po 5 losowań, z reklamami jednej kampanii, szablonu, strony albo płatnika zawsze po tej samej stronie podziału. Od progu 0,7 łapie średnio 74 z 95 oszustw bez fałszywego alarmu, od progu 0,3 kieruje do człowieka 90 z 95 przy 8 fałszywych alarmach na 374. Świeży test po wyborze modelu: 24 opublikowane oszustwa, wszystkie od 0,3 w górę (19 od 0,7), i 153 zwykłe reklamy bez fałszywego alarmu. Inne modele na tych samych cechach (naiwny Bayes, SVM) wypadają w granicach szumu, a reguły na słowach kluczowych łapią 23 z 95. Reklamę wideo model ocenia po tekście posta i jednej klatce. Gdy do reklamy doda się nagranie (`PUT /reklamy/{id}/nagranie`), mowę zamienia na tekst otwarty model Whisper na procesorze (około 0,4 s na sekundę nagrania), a KAPSEL ocenia ją razem z tekstem posta. Mowa może podnieść ryzyko, ale nie obniża ryzyka samego tekstu posta. Zbieracze nie pobierają filmów, a trafności dla polskiej mowy na prawdziwych reklamach jeszcze nie zmierzyliśmy. Model uczył się na polskich reklamach, więc oszustwa po angielsku, w tekście albo w mowie, dostają niską ocenę.

To małe próby: pokazują kierunek, nie dokładny odsetek.

## Uruchomienie

Potrzebny jest Docker z Compose. Karta graficzna nie jest potrzebna. Obrazy zajmują około 8 GB na dysku, a działające usługi około 2 GB pamięci. Pierwsze budowanie pobiera biblioteki oraz modele do odczytu tekstu z obrazów i do zamiany mowy na tekst; na laptopie z 8-rdzeniowym procesorem najdłuższy obraz (odczyt) budował się około 6,5 minuty, nie licząc pobierania obrazów bazowych.

```
cp .env.example .env
```

W pliku `.env` ustaw własne hasło bazy, a potem uruchom usługi:

```
docker compose up -d --build
```

Przy pierwszym starcie baza zapisuje to hasło i wczytuje dane pokazowe zebrane 21–22.11.2026 z `baza/dane_pokazowe.sql.gz`: reklamy z Google, Meta, TikToka i YouTube, strony doradców oraz 32 oszustwa z ostrzeżeń CSIRT KNF. Obrazy reklam pochodzą z publicznych bibliotek reklam i z ostrzeżeń CSIRT KNF; prawa do nich mają ich autorzy, a tutaj służą wyłącznie jako materiał do analizy. Hasło zmienione później w `.env` zadziała dopiero po wyczyszczeniu bazy przez `docker compose down -v`.

Panel i API nie mają logowania; po starcie są dostępne tylko z tego komputera.

- Panel: http://localhost:8080
- Opis API w przeglądarce: http://localhost:8000/docs
- Czysty start bazy: `docker compose down -v` kasuje bazę razem z tym, czego model nauczył się od analityka, i dodanymi rodzajami oszustw; kolejny `docker compose up -d` wczytuje dane pokazowe od nowa.

Zmienne `DUZY_MODEL_URL`, `DUZY_MODEL_NAZWA` i `DUZY_MODEL_KLUCZ` w `.env` są opcjonalne: wskazują duży model, który daje drugą ocenę niepewnych reklam i pisze przykłady dla nowych rodzajów oszustw. Bez nich te dwie funkcje są wyłączone. Adres to pełny adres zapytań chat completions serwera zgodnego z API OpenAI, także lokalnego vLLM, llama.cpp albo Ollamy. Sama ocena reklam nie potrzebuje dużego modelu.

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

Zmienne `ZBIERACZ_USER_AGENTS` i `ZBIERACZ_PROXY` w `.env` są opcjonalne: listy oddzielone znakiem `|`, z których każde kolejne zadanie bierze następną wartość. Puste oznaczają własny User-Agent przeglądarki i brak proxy. Strona, która odmawia, nie jest odpytywana ponownie.

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

Test z katalogu `testy` uruchamia się na komputerze przez `uv` i wymaga działających usług. Reklamy testowe, które dodaje do bazy, usuwa na końcu. Model zostawia taki, jaki był.

GitHub Actions (`.github/workflows/sprawdzenie.yml`) przy każdym pushu i pull requeście buduje panel, uruchamia testy `ai` i `zbieracz`, które nie potrzebują działających usług, i skanuje zależności (`npm audit`, `pip-audit`). Dependabot (`.github/dependabot.yml`) co tydzień proponuje aktualizacje bibliotek, obrazów Dockera i akcji.

## Gdzie co dopisać

- Nowe źródło reklam: nowy plik w `zbieracz/`, który wysyła rekordy na `POST /reklamy`.
- Nowy sygnał: własny plik w `ai/` na wzór `wymogi.py`, z testem, dołączony do listy `sygnaly` w `/ocen` (`ai/main.py`).
- Nowe pole reklamy: `baza/schemat.sql`, `api/schematy.py`, `KONTRAKT.md`.
