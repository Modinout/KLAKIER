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
| `rejestr` | obiekt lub null | czy płatnik reklamy jest na listach KNF (domy maklerskie, banki maklerskie, oddziały zagranicznych firm, zagraniczne firmy notyfikowane); null, gdy reklama nie podaje płatnika. Pola: `stan`, `podmiot`, `panstwo`, `lista` |
| `sygnaly` | lista | co znalazł zbieracz, a potem co znalazły moduły; każdy sygnał ma `modul`, `kod`, `opis`, `podstawa`; sygnały zbieracza zostają przy każdym ponownym ocenianiu; sygnał `wielu_platnikow_domeny` (moduł `M1`) oznacza, że reklamy tej samej `domena` opłaca co najmniej trzech różnych płatników, którzy nie są w rejestrze KNF i nie mają w nazwie marki z domeny. Api liczy go przy każdym odczycie ze wszystkich reklam domeny i nie zapisuje go w bazie, więc dostają go też starsze reklamy domeny, gdy przybędzie płatnik; sygnał `obca_domena` (moduł `M1`) oznacza, że płatnik ma nazwę marki z rejestru KNF, ale reklama prowadzi do domeny bez tej nazwy, czyli do strony innej marki. Api też liczy go przy każdym odczycie |
| `powody` | lista | słowa, które najmocniej wpłynęły na ocenę; każde ma `slowo` i `waga`; pusta przy ryzyku poniżej 0,1 |
| `rodzaj` | tekst lub null | rodzaj oszustwa według modelu, np. jeden z `GET /rodzaje` |
| `drugi_sedzia` | obiekt lub null | ocena dużego modelu, gdy mały nie jest pewny: `werdykt`, `uzasadnienie`; null, gdy duży model nie jest ustawiony |
| `status` | `nowa`, `w_toku`, `zamknieta` | etap pracy analityka |
| `werdykt_analityka` | `ok`, `do_sprawdzenia`, `oszustwo` lub null | werdykt analityka; z tych werdyktów model uczy się przez `POST /ucz` |
| `ma_obraz` | prawda / fałsz | czy reklama ma obraz pod `GET /reklamy/{id}/obraz` |
| `poziom` | `wysokie`, `srednie`, `niskie` | jeden poziom ryzyka z sygnałów i werdyktu, liczony przy każdym odczycie, nie zapisywany w bazie: `wysokie`, gdy jest twarde ustalenie (domena z listy ostrzeżeń KNF, kopia ostrzeżonej strony, domena opłacana przez wielu niepowiązanych płatników, płatnik spoza rejestru albo poza listami KNF, doradztwo bez zezwolenia) albo treść jest typowa dla fałszywych inwestycji (werdykt `oszustwo`); `srednie`, gdy jest inny sygnał, czyli naruszenie zasad reklamy przez firmę z rejestru; `niskie`, gdy nie ma ustaleń (sam werdykt `do_sprawdzenia` poziomu nie podnosi); sygnały o liście CERT (`brak_na_liscie_cert`, `na_liscie_cert`) to notatki i poziomu nie podnoszą |
| `powod` | tekst lub null | jedno zdanie, które decyduje o poziomie: `opis` najmocniejszego sygnału albo zdanie o ocenie tekstu; null przy poziomie `niskie` |

## Adresy api

| Adres | Co robi |
| --- | --- |
| `POST /reklamy` | dodaje reklamę i od razu ją ocenia |
| `GET /reklamy?werdykt=&status=&min_ryzyko=&od=` | lista od największego ryzyka; każdy filtr można pominąć; `od` (data i czas ISO 8601) zostawia tylko reklamy z `dodano` późniejszym niż `od`, więc panel po pierwszej pełnej liście pyta z `od` równym najnowszemu `dodano`, jakie ma |
| `GET /reklamy/{id}` | jedna reklama |
| `PATCH /reklamy/{id}` | zmiana statusu, werdyktu analityka lub domeny, treść: `{"status": "w_toku"}`, `{"werdykt_analityka": "oszustwo"}`, `{"domena": "www.pekao.com.pl"}` albo kilka z tych pól; zmieniają się tylko wysłane pola, `"werdykt_analityka": null` go kasuje, `"domena": null` też; zmiana domeny nie ocenia reklamy od nowa |
| `GET /reklamy/{id}/podobne` | do 50 innych reklam o podobnym początku tekstu (pierwsze 1000 znaków, `podobienstwo` od 0.5 do 1), od najbardziej podobnej; `503`, gdy szukanie trwa ponad 5 s |
| `PUT /reklamy/{id}/obraz` | zapisuje obraz reklamy, treść: `{"obraz": "..."}` (PNG albo JPEG w base64), drugi obraz zastępuje pierwszy; gdy reklama ma pusty `tekst`, odczytuje go z obrazu i ocenia reklamę od nowa, reklama z tekstem go zachowuje; zwraca pełną reklamę; `404`, gdy nie ma reklamy, `422`, gdy to nie jest PNG ani JPEG, `503`, gdy tekst trzeba było odczytać, a usługa `odczyt` nie działa |
| `GET /reklamy/{id}/obraz` | obraz reklamy z typem `image/png` albo `image/jpeg`; `404`, gdy reklama nie ma obrazu |
| `POST /ucz` | uczy model na reklamach z `werdykt_analityka` i ocenia od nowa wszystkie reklamy; zwraca `przyklady`, `przeliczono` |
| `GET /rodzaje` | lista rodzajów oszustw, które zna model |
| `POST /rodzaje` | dodaje rodzaj oszustwa, treść: `{"nazwa": "...", "opis": "..."}`, i ocenia od nowa wszystkie reklamy; zwraca `nazwa`, `przyklady`, `przeliczono`; `409`, gdy taki rodzaj już jest, `503`, gdy nie ma dużego modelu |
| `GET /progi` | dane dla suwaka progu: ile oszustw łapie dany próg i ile daje fałszywych alarmów |
| `POST /odczytaj` | odczytuje tekst z obrazu reklamy, opis wyżej w „Tekst z obrazu reklamy” |
| `/alerty` (WebSocket) | po każdej nowej reklamie (`POST /reklamy` z odpowiedzią `201`) z poziomem `wysokie` wysyła każdemu połączonemu klientowi jedną wiadomość JSON: `{"id", "reklamodawca", "ryzyko", "werdykt", "zrodlo", "dodano", "poziom", "powod"}`; klient nic nie wysyła |

Panel woła te same adresy z przedrostkiem `/api`.

### Pole `rejestr`

| `stan` | Znaczenie | `podmiot`, `panstwo`, `lista` |
| --- | --- | --- |
| `w_rejestrze` | nazwa płatnika to nazwa wpisu z list KNF | ten wpis: nazwa jak na liście, państwo, nazwa listy |
| `spoza_rejestru` | płatnika nie ma na listach, ale jego marka ma tam inny podmiot, np. `Tickmill Ltd` i `Tickmill Europe Ltd` | wpis tej marki |
| `tfi` | płatnik to towarzystwo funduszy inwestycyjnych, a list TFI tu nie ma | null |
| `bank` | płatnik to bank spoza listy banków z działalnością maklerską, a rejestru banków tu nie ma | null |
| `poza_listami` | ani płatnika, ani jego marki nie ma na listach | null |

`lista` to jedna z `domy_maklerskie`, `banki_maklerskie`, `oddzialy_zagranicznych_firm`, `notyfikowane_zagraniczne`. Stany `spoza_rejestru` i `poza_listami` dają też sygnał modułu `M1` w `sygnaly`.

## Adresy ai

| Adres | Co robi |
| --- | --- |
| `POST /ocen` | przyjmuje `tekst`, `reklamodawca`, `url`, `zrodlo` (dla `youtube` i `strony_doradcow` nazwa to autor materiału, a nie płatnik reklamy, więc rejestr nie daje ustalenia `M1`; dla `youtube` tekstu nie ocenia też model: werdykt `ok`, ryzyko 0); zwraca `werdykt`, `ryzyko`, `pewny`, `rejestr`, `sygnaly`, `powody`, `rodzaj` |
| `POST /drugi_sedzia` | przyjmuje `tekst`; zwraca `werdykt`, `uzasadnienie` od dużego modelu; `503`, gdy go nie ma albo nie odpowiedział |
| `POST /ucz` | przyjmuje `przyklady` (lista `tekst`, `werdykt`), zastępuje nimi wszystkie przykłady analityka i uczy model od nowa; zwraca `przyklady`, `razem` |
| `GET /rodzaje` | lista nazw rodzajów oszustw |
| `POST /rodzaje` | przyjmuje `nazwa`, `opis`; duży model pisze przykłady, model uczy się nowego rodzaju; zwraca `nazwa`, `przyklady`; `409`, gdy nazwa już jest, `503`, gdy nie ma dużego modelu |
| `GET /progi` | tabela progów z `ai/progi.csv` |
