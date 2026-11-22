# Kontrakt danych

Jedno miejsce, w którym usługi uzgadniają kształt danych. Zmiana tutaj oznacza zmianę w `baza/schemat.sql` i `api/schematy.py`.

## Reklama od zbieracza

`POST /reklamy`

| Pole | Typ | Opis |
| --- | --- | --- |
| `zrodlo` | tekst | skąd pochodzi rekord, np. `plik`, `google_ads` |
| `id_zrodla` | tekst | identyfikator reklamy w źródle; para `zrodlo` + `id_zrodla` jest unikalna |
| `platforma` | tekst | gdzie reklamę wyświetlono, np. `facebook`, `google` |
| `url` | tekst lub null | adres rekordu w źródle, np. strona reklamy w bibliotece reklam |
| `domena` | tekst lub null, można pominąć | domena, do której prowadzi reklama, sama nazwa hosta małymi literami, np. `www.pekao.com.pl`; null, gdy nie wiadomo |
| `reklamodawca` | tekst lub null | nazwa podana w reklamie |
| `tekst` | tekst | treść reklamy |
| `zebrano` | data i czas (ISO 8601) | kiedy zbieracz ją zapisał |
| `opublikowano` | data (`RRRR-MM-DD`) lub null, można pominąć | dzień, w którym materiał opublikowano albo pierwszy raz pokazano |
| `sygnaly` | lista, można pominąć | co znalazł sam zbieracz; każdy sygnał ma `modul`, `kod`, `opis`, `podstawa` |

Odpowiedź: `201` i pełna reklama, albo `409`, gdy taka reklama już jest w bazie. Ten i każdy inny adres odpowiada `503`, gdy usługa `ai` albo `odczyt` nie odpowiada.

## Tekst z obrazu reklamy

`POST /odczytaj`

| Pole | Typ | Opis |
| --- | --- | --- |
| `obraz` | tekst | obraz reklamy w PNG albo JPEG, zakodowany w base64 |

Odpowiedź: `200` i `{"tekst": "..."}`, `422`, gdy to nie jest obraz, albo `503`, gdy usługa `odczyt` nie działa. Odczytany tekst wysyła się potem jako `tekst` w `POST /reklamy`.

## Nagranie reklamy wideo

`PUT /reklamy/{id}/nagranie` od analityka, który ma nagranie reklamy wideo.

| Pole | Typ | Opis |
| --- | --- | --- |
| `nagranie` | tekst | plik mp4, mp3, wav, m4a albo webm, zakodowany w base64, do 50 MB pliku |

Api wysyła nagranie do usługi `odczyt`, zapisuje odczytaną mowę w polu `mowa` reklamy, ocenia reklamę od nowa z tą mową i dopisuje jeden wpis do historii. Nowe nagranie zastępuje poprzednią mowę. Odpowiedź: `200` i pełna reklama, `404`, gdy nie ma reklamy, `422`, gdy nagranie jest większe niż 50 MB albo `odczyt` uznaje, że to nie dźwięk, albo `503`, gdy usługa `odczyt` nie działa.

## Pomiar strony docelowej

`PUT /strony/{domena}` od `zbieracz/strony_docelowe.py`, który otwiera stronę główną domeny na komputerze (okno 1366 × 900), na tablecie (okno 768 × 1024) i na telefonie (okno 390 × 844, User-Agent przeglądarki bez zmian). Nowy pomiar domeny zastępuje poprzedni. Taki sam pomiar strony pod linkiem, ale bez tabletu, wysyła sprawdzenie linku z panelu, opis niżej w „Sprawdzenie linku z panelu”.

| Pole | Typ | Opis |
| --- | --- | --- |
| `komputer`, `tablet`, `telefon` | obiekt lub null | pomiar w jednym widoku; null, gdy strona się w nim nie otworzyła; `tablet` można pominąć |
| `adres` | tekst | adres strony po przekierowaniach |
| `przewazajacy_px` | liczba | rozmiar czcionki, którym napisano najwięcej widocznego tekstu |
| `cfd` | prawda / fałsz | czy widoczny tekst strony mówi o kontraktach CFD |
| `ostrzezenie` | obiekt lub null | najbardziej widoczna kopia standardowego ostrzeżenia o ryzyku CFD; null, gdy go nie ma. Pola: `tekst`, `px`, `pogrubienie`, `kontrast` (według WCAG, od 1 do 21; null, gdy za tekstem jest obraz albo gradient), `widoczne`, `bez_przewijania` |

Odpowiedź: `200` i zapisany pomiar z `domena` i `zmierzono`.

## Data rejestracji domeny

`PUT /domeny/{domena}` od `zbieracz/wiek_domen.py`, który dla każdej domeny docelowej reklam pyta RDAP (`https://rdap.org/domain/<domena>`, z przekierowaniem do rejestru) o domenę zarejestrowaną w rejestrze, np. `pekao.com.pl` dla `www.pekao.com.pl`, najwyżej raz na sekundę. Klucz `{domena}` to `domena` reklamy. Nowa data domeny zastępuje poprzednią.

| Pole | Typ | Opis |
| --- | --- | --- |
| `zarejestrowano` | data (`RRRR-MM-DD`) | dzień rejestracji domeny według RDAP |

Odpowiedź: `200` i zapisana data z `domena` i `sprawdzono`.

## Reklama w bazie i w panelu

Pola jak wyżej oraz:

| Pole | Typ | Opis |
| --- | --- | --- |
| `id` | liczba | numer w bazie |
| `dodano` | data i czas | kiedy trafiła do bazy |
| `opublikowano` | data lub null | jak od zbieracza; null, gdy zbieracz go nie podał |
| `domena` | tekst lub null | dokąd prowadzi reklama; `url` zostaje adresem rekordu w źródle; można ją uzupełnić przez `PATCH /reklamy/{id}` |
| `werdykt` | `ok`, `do_sprawdzenia`, `oszustwo` | z ryzyka: poniżej 0,3 `ok`, od 0,7 `oszustwo`, pomiędzy albo bez tekstu `do_sprawdzenia` |
| `ryzyko` | liczba 0-1 | prawdopodobieństwo oszustwa |
| `pewny` | prawda / fałsz | fałsz przy werdykcie `do_sprawdzenia`: ocenić powinien człowiek |
| `rejestr` | obiekt lub null | czy płatnik reklamy jest w rejestrach KNF (domy maklerskie, banki maklerskie, oddziały zagranicznych firm, zagraniczne firmy notyfikowane); null, gdy reklama nie podaje płatnika. Pola: `stan`, `podmiot`, `panstwo`, `lista` |
| `sygnaly` | lista | co znalazł zbieracz, a potem co znalazły moduły; każdy sygnał ma `modul`, `kod`, `opis`, `podstawa`; sygnał `polecenie_bez_oznaczenia` z linkiem do polecanej firmy ma też `firma` = `{"nazwa", "domena", "stan_rejestru"}` (`stan_rejestru` jak `rejestr.stan` albo null), u innych sygnałów `firma` jest null; sygnały zbieracza zostają przy każdym ponownym ocenianiu; sygnał `wielu_platnikow_domeny` (moduł `M1`) oznacza, że reklamy tej samej `domena` opłaca co najmniej trzech różnych płatników, którzy nie są w rejestrze KNF i nie mają w nazwie marki z domeny. Api liczy go przy każdym odczycie ze wszystkich reklam domeny i nie zapisuje go w bazie, więc dostają go też starsze reklamy domeny, gdy przybędzie płatnik; sygnał `obca_domena` (moduł `M1`) oznacza, że płatnik ma nazwę marki z rejestru KNF, ale reklama prowadzi do domeny bez tej nazwy, czyli do strony innej marki. Api też liczy go przy każdym odczycie; sygnały modułu `M2` z pomiaru strony domeny (`PUT /strony/{domena}`), też liczone przy każdym odczycie: `ostrzezenie_nieczytelne`, gdy ostrzeżenie o ryzyku CFD jest mniejsze niż przeważający tekst, ma kontrast poniżej 4,5:1 (3:1 przy dużym tekście) albo nie widać go w jednym z widoków, i `brak_ostrzezenia_strony`, gdy strona mówi o CFD, a ostrzeżenia nie widać w żadnym widoku; sygnał `mloda_domena` (moduł `M1`) z daty rejestracji domeny (`PUT /domeny/{domena}`), też liczony przy każdym odczycie: reklama o inwestycjach (ten sam test tematu co w `ai`, na tekście i nazwie płatnika) prowadzi do domeny zarejestrowanej mniej niż 30 dni przed `opublikowano`, a bez tej daty przed dniem odczytu; domena zarejestrowana po tym dniu sygnału nie daje |
| `powody` | lista | słowa, które najmocniej wpłynęły na ocenę; każde ma `slowo` i `waga`; pusta przy ryzyku poniżej 0,1 |
| `rodzaj` | tekst lub null | rodzaj oszustwa według modelu, np. jeden z `GET /rodzaje` |
| `status` | `nowa`, `w_toku`, `zamknieta` | etap pracy analityka |
| `werdykt_analityka` | `ok`, `do_sprawdzenia`, `oszustwo` lub null | werdykt analityka; z tych werdyktów model uczy się przez `POST /ucz` |
| `notatka` | tekst lub null | notatka analityka do sprawy; null, dopóki nikt jej nie napisze |
| `ma_obraz` | prawda / fałsz | czy reklama ma obraz pod `GET /reklamy/{id}/obraz` |
| `mowa` | tekst lub null | mowa z nagrania reklamy wideo, dodana przez `PUT /reklamy/{id}/nagranie`; model ocenia ją razem z tekstem; null, dopóki nikt nie dodał nagrania |
| `poziom` | `wysokie`, `srednie`, `niskie` | jeden poziom ryzyka z sygnałów i ryzyka, liczony przy każdym odczycie, nie zapisywany w bazie: `wysokie`, gdy jest twarde ustalenie (domena z listy ostrzeżeń KNF, kopia ostrzeżonej strony, domena opłacana przez wielu niepowiązanych płatników, marka z rejestru płacąca za cudzą domenę, płatnik poza listami KNF, doradztwo bez zezwolenia, reklama z listy oszustw CSIRT KNF) albo treść jest typowa dla fałszywych inwestycji (reklama ma tekst, a jej `ryzyko` jest co najmniej progiem z `GET /prog`; przy domyślnym progu 0,7 to te same reklamy co z werdyktem `oszustwo`); `srednie`, gdy jest inny sygnał, czyli naruszenie zasad reklamy przez firmę z rejestru; `niskie`, gdy nie ma ustaleń (samo ryzyko poniżej progu poziomu nie podnosi); sygnały o liście CERT (`brak_na_liscie_cert`, `na_liscie_cert`) i płatnik będący inną spółką marki z rejestru (`platnik_spoza_rejestru`) to notatki i poziomu nie podnoszą |
| `powod` | tekst lub null | jedno zdanie, które decyduje o poziomie: `opis` najmocniejszego sygnału albo zdanie o ocenie tekstu; null przy poziomie `niskie` |

## Adresy api

| Adres | Co robi |
| --- | --- |
| `POST /reklamy` | dodaje reklamę i od razu ją ocenia |
| `GET /reklamy?werdykt=&status=&min_ryzyko=&od=` | lista od największego ryzyka; każdy filtr można pominąć; `od` (data i czas ISO 8601) zostawia tylko reklamy z `dodano` późniejszym niż `od`, więc panel po pierwszej pełnej liście pyta z `od` równym najnowszemu `dodano`, jakie ma |
| `GET /reklamy/{id}` | jedna reklama |
| `PATCH /reklamy/{id}` | zmiana statusu, werdyktu analityka, domeny lub notatki, treść: `{"status": "w_toku"}`, `{"werdykt_analityka": "oszustwo"}`, `{"domena": "www.pekao.com.pl"}`, `{"notatka": "..."}` albo kilka z tych pól; zmieniają się tylko wysłane pola, `"werdykt_analityka": null` go kasuje, `"domena": null` i `"notatka": null` też; zmiana domeny nie ocenia reklamy od nowa; każde zmienione pole dopisuje wpis do historii, opis niżej w „Historia zmian” |
| `GET /reklamy/{id}/historia` | historia zmian reklamy od najnowszej, opis niżej w „Historia zmian”; `404`, gdy nie ma reklamy |
| `GET /reklamy/{id}/podobne` | do 50 innych reklam o podobnym początku tekstu (pierwsze 1000 znaków, `podobienstwo` od 0.5 do 1), od najbardziej podobnej; `503`, gdy szukanie trwa ponad 5 s |
| `GET /reklamy/{id}/powiazane` | inne reklamy, których `tekst` ma ten sam numer telefonu albo adres komunikatora, od najstarszej: lista `{"id", "tytul", "powod", "wartosc"}`, jedna pozycja na reklamę; `tytul` jak tytuł sprawy w panelu (domena z ostrzeżenia KNF, płatnik, domena docelowa, pierwsza domena z tekstu albo `Reklama bez nadawcy`); `powod` `ten_sam_telefon` z numerem w `wartosc` jako `+` i same cyfry (polski numer z 9 cyfr dostaje `+48`), albo `ten_sam_komunikator` z adresem `t.me/nazwa` (nazwa małymi literami), `t.me/+kod` (zaproszenie) lub `wa.me/cyfry`; daty, kwoty, numery NIP, REGON, KRS, PESEL i kont, cyfry w adresach stron i wzory z formularzy (np. `+48 512 345 678`) numerami nie są; gdy reklamy łączy kilka kontaktów, `powod` i `wartosc` dotyczą jednego z nich; `404`, gdy nie ma reklamy |
| `PUT /reklamy/{id}/obraz` | zapisuje obraz reklamy, treść: `{"obraz": "..."}` (PNG albo JPEG w base64), drugi obraz zastępuje pierwszy; gdy reklama ma pusty `tekst`, odczytuje go z obrazu i ocenia reklamę od nowa, reklama z tekstem go zachowuje; zwraca pełną reklamę; `404`, gdy nie ma reklamy, `422`, gdy to nie jest PNG ani JPEG, `503`, gdy tekst trzeba było odczytać, a usługa `odczyt` nie działa |
| `PUT /reklamy/{id}/nagranie` | zamienia nagranie reklamy wideo na `mowa` i ocenia reklamę od nowa, opis wyżej w „Nagranie reklamy wideo” |
| `GET /reklamy/{id}/obraz` | obraz reklamy z typem `image/png` albo `image/jpeg`; `404`, gdy reklama nie ma obrazu |
| `POST /ucz` | uczy model na reklamach z `werdykt_analityka` i ocenia od nowa wszystkie reklamy; każdej reklamie, której zmienił się werdykt albo poziom, dopisuje wpis do historii; zwraca `przyklady`, `przeliczono` |
| `GET /rodzaje` | lista rodzajów oszustw, które zna model |
| `GET /progi` | dane dla suwaka progu: ile oszustw łapie dany próg i ile daje fałszywych alarmów |
| `GET /prog` | zapisany próg ryzyka: `{"prog": 0.7}`; od niego tekst reklamy sam daje poziom `wysokie`, a z nim alert; werdykt zostaje taki, jak dał model |
| `PUT /prog` | zapisuje próg, treść: `{"prog": 0.6}`, liczba większa od 0 i mniejsza od 1; zwraca zapisany próg; działa od razu na poziom wszystkich reklam; `422` dla progu spoza przedziału |
| `POST /odczytaj` | odczytuje tekst z obrazu reklamy, opis wyżej w „Tekst z obrazu reklamy” |
| `PUT /domeny/{domena}` | zapisuje datę rejestracji domeny, opis wyżej w „Data rejestracji domeny” |
| `PUT /strony/{domena}` | zapisuje pomiar ostrzeżenia o ryzyku na stronie domeny, opis wyżej w „Pomiar strony docelowej” |
| `POST /sprawdz` | zleca sprawdzenie linku, opis niżej w „Sprawdzenie linku z panelu” |
| `GET /sprawdz/{id}` | stan sprawdzenia linku; `404`, gdy go nie ma |
| `PUT /sprawdz/{id}` | robotnik zapisuje stan sprawdzenia, treść jak odpowiedź `GET /sprawdz/{id}`; `404`, gdy go nie ma |
| `POST /reklamy/{id}/dowody` | robotnik dopisuje dowód wizyty, opis niżej w „Dowody wizyty”; zwraca go bez plików; `404`, gdy nie ma reklamy, `422`, gdy `obraz` to nie PNG |
| `GET /reklamy/{id}/dowody` | dowody reklamy od najstarszego, bez plików; `404`, gdy nie ma reklamy |
| `GET /dowody/{id}/obraz` | zrzut ekranu z dowodu, `image/png`; `404`, gdy nie ma dowodu |
| `GET /dowody/{id}/html` | kod strony z dowodu jako plik do zapisania (`text/plain`, `Content-Disposition: attachment`), nigdy do wyświetlenia; `404`, gdy nie ma dowodu |
| `GET /reklamy/{id}/paczka` | ZIP z plikami wszystkich dowodów reklamy i `manifest.json` z ich skrótami SHA-256; `404`, gdy nie ma reklamy |
| `/alerty` (WebSocket) | po każdej nowej reklamie (`POST /reklamy` z odpowiedzią `201`) z poziomem `wysokie` wysyła każdemu połączonemu klientowi jedną wiadomość JSON: `{"id", "reklamodawca", "ryzyko", "werdykt", "zrodlo", "dodano", "poziom", "powod"}`; klient nic nie wysyła |

Panel woła te same adresy z przedrostkiem `/api`.

### Pole `rejestr`

| `stan` | Znaczenie | `podmiot`, `panstwo`, `lista` |
| --- | --- | --- |
| `w_rejestrze` | nazwa płatnika to nazwa wpisu z rejestrów KNF | ten wpis: nazwa jak w rejestrze, państwo, nazwa rejestru |
| `spoza_rejestru` | płatnika nie ma na listach, ale jego marka ma tam inny podmiot, np. `Tickmill Ltd` i `Tickmill Europe Ltd` | wpis tej marki |
| `mica` | płatnik to dostawca usług w zakresie kryptoaktywów z licencją MiCA w innym państwie UE (rejestr ESMA) | ten wpis: nazwa, kod państwa, `mica` |
| `tfi` | płatnik to towarzystwo funduszy inwestycyjnych, a list TFI tu nie ma | null |
| `bank` | płatnik to bank spoza listy banków z działalnością maklerską, a rejestru banków tu nie ma | null |
| `poza_listami` | ani płatnika, ani jego marki nie ma w rejestrach KNF ani w rejestrze MiCA | null |

`lista` to jedna z `domy_maklerskie`, `banki_maklerskie`, `oddzialy_zagranicznych_firm`, `notyfikowane_zagraniczne`. Stany `spoza_rejestru` i `poza_listami` dają też sygnał modułu `M1` w `sygnaly`; `poza_listami` tylko wtedy, gdy tekst lub nazwa płatnika dotyczy inwestowania.

## Historia zmian

`GET /reklamy/{id}/historia` zwraca listę wpisów od najnowszego.

| Pole | Typ | Opis |
| --- | --- | --- |
| `kiedy` | data i czas | kiedy zapisano zmianę |
| `kto` | tekst | nazwa z nagłówka `X-Analityk`; bez nagłówka `analityk`, a przy `POST /ucz` `model` |
| `co` | tekst | jedno krótkie zdanie o zmianie |

Panel nie wysyła nagłówka `X-Analityk`, więc jego zmiany mają `kto` = `analityk`. Inny klient api może podać w nim nazwę, zakodowaną jak część adresu (`encodeURIComponent`), bo nagłówek nie przeniesie liter takich jak ł. `PATCH` dopisuje wpis na każde wysłane pole, którego wartość się zmieniła: `Status: nowa → w toku`, `Ocena analityka: oszustwo` albo `Ocena analityka usunięta`, `Domena: www.pekao.com.pl` albo `Domena usunięta`, `Notatka zmieniona` albo `Notatka usunięta`. `POST /ucz` dopisuje jeden wpis każdej reklamie, której zmienił się `werdykt` albo `poziom`, np. `Ocena modelu: ok → oszustwo, poziom ryzyka: niskie → wysokie`.

## Sprawdzenie linku z panelu

Analityk wkleja link w panelu. `POST /sprawdz` z treścią `{"url": "https://..."}` zapisuje sprawdzenie i wstawia je do kolejki Valkey `patrol:linki`. Bierze z niej usługa `sprawdzacz` (`zbieracz/robotnik.py linki`), która obsługuje tylko linki, więc link nie czeka na domenę patrolu; robotnik patrolu też bierze linki przed swoimi domenami. Odpowiedź: `202` i `{"id": 12}`, `422`, gdy adres nie zaczyna się od `http://` ani `https://` albo wskazuje sieć wewnętrzną (nazwa bez kropki, `localhost`, `*.local`, `*.internal`, adres prywatny), albo `503`, gdy kolejka nie działa. Robotnik nie otwiera adresów sieci wewnętrznej także po przekierowaniu ani w obrazkach i skryptach strony; takie sprawdzenie kończy się stanem `blad`.

Robotnik otwiera link na komputerze (okno 1366 × 900) i na telefonie (okno 390 × 844, User-Agent przeglądarki bez zmian), idzie za przekierowaniami, a potem:

- mierzy ostrzeżenie o ryzyku na otwartej stronie jak `zbieracz/strony_docelowe.py` i wysyła pomiar przez `PUT /strony/{domena}` dla domeny po przekierowaniach,
- dodaje stronę przez `POST /reklamy`: `zrodlo` `panel`, `id_zrodla` i `url` to wklejony link, `platforma` `www`, `domena` to host po przekierowaniach, `tekst` to tytuł strony i do 1500 pierwszych znaków jej widocznego tekstu; `sygnaly` jak w patrolu: `reklama_domeny_z_ostrzezenia_knf`, gdy któraś domena z łańcucha przekierowań jest na liście ostrzeżeń publicznych KNF, i sygnał listy CERT Polska dla domeny po przekierowaniach; api ocenia ją i wysyła alert jak przy każdej reklamie,
- dopisuje reklamie dowód każdego widoku przez `POST /reklamy/{id}/dowody`,
- zapisuje zrzut ekranu z komputera jako obraz reklamy, gdy reklama nie ma jeszcze obrazu.

Ten sam link wklejony drugi raz trafia do tej samej reklamy i dopisuje jej nowe dowody. Strona, która odpowiada kodem 4xx albo 5xx, nie otwiera się w 30 s albo zamiast treści pokazuje sprawdzenie, czy odwiedza ją człowiek, kończy sprawdzenie stanem `blad` bez reklamy.

`GET /sprawdz/{id}` zwraca:

| Pole | Typ | Opis |
| --- | --- | --- |
| `stan` | `w_kolejce`, `w_toku`, `gotowe`, `blad` | etap sprawdzenia |
| `reklama_id` | liczba lub null | reklama ze strony pod linkiem, przy stanie `gotowe` |
| `blad` | tekst lub null | krótki powód po polsku przy stanie `blad`, np. `Strona odpowiedziała kodem błędu 404.` |

### Dowody wizyty

Dowody się tylko dopisuje: żadnego się nie zmienia ani nie zastępuje. `POST /reklamy/{id}/dowody` od robotnika przyjmuje `kiedy`, `rodzaj`, `adres`, `lancuch`, `obraz` (zrzut całej strony, PNG w base64) i `html` (kod strony po wczytaniu); skróty SHA-256 api liczy z bajtów, które zapisuje. `GET /reklamy/{id}/dowody` zwraca dowody bez plików:

| Pole | Typ | Opis |
| --- | --- | --- |
| `id` | liczba | numer dowodu |
| `kiedy` | data i czas | kiedy przeglądarka otworzyła link |
| `rodzaj` | `komputer`, `telefon` | widok przeglądarki |
| `adres` | tekst | adres strony po przekierowaniach |
| `lancuch` | lista tekstów | adresy, które otwierała główna ramka strony, od wklejonego linku po ostatnie przekierowanie |
| `sha256` | obiekt | `obraz` i `html`: skrót SHA-256 każdego pliku zapisany szesnastkowo |

`GET /reklamy/{id}/paczka` zwraca ZIP z plikami `{id}-{rodzaj}.png` i `{id}-{rodzaj}.html` każdego dowodu oraz `manifest.json`: `reklama_id`, `url` i `dowody`, każdy z polami jak wyżej i listą `pliki` (`plik`, `sha256`).

## Adresy ai

| Adres | Co robi |
| --- | --- |
| `POST /ocen` | przyjmuje `tekst`, `reklamodawca`, `url`, `zrodlo` (dla `youtube` i `strony_doradcow` nazwa to autor materiału, a nie płatnik reklamy, więc rejestr nie daje ustalenia `M1`; dla `youtube` tekstu nie ocenia też model: werdykt `ok`, ryzyko 0); zwraca `werdykt`, `ryzyko`, `pewny`, `rejestr`, `sygnaly`, `powody`, `rodzaj` |
| `POST /ucz` | przyjmuje `przyklady` (lista `tekst`, `werdykt`), zastępuje nimi wszystkie przykłady analityka i uczy model od nowa; zwraca `przyklady`, `razem` |
| `GET /rodzaje` | lista nazw rodzajów oszustw |
| `GET /progi` | tabela progów z `ai/progi.csv` |
