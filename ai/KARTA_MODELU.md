# Karta modelu KAPSEL: mały klasyfikator reklam (pierwsze sito)

KAPSEL (Kompaktowy Algorytm Przesiewowy Szybko Etykietujący Lokalnie). Stan na 2026-11-22, wersja 5 (95 prawdziwych oszustw w nauce, odporność na sztuczki z pisownią, model rozróżnia: oszustwo albo nie).

## Co robi

Dostaje tekst reklamy i zwraca werdykt `ok` / `do_sprawdzenia` / `oszustwo`, prawdopodobieństwa i flagę `pewny`.
Działa na samym procesorze, w milisekundach, bez internetu. Gdy `pewny` jest fałszem, reklamę ocenia człowiek.
Model układa kolejkę dla analityka. Nie rozstrzyga sprawy: o tym decydują fakty (kto płaci, czy firma jest w rejestrze KNF).

```python
from przewidz import przewidz
przewidz('Zainwestuj 900 zł i zarabiaj 20 000 zł miesięcznie')
# {'werdykt': 'oszustwo', 'prawdopodobienstwa': {...}, 'pewny': True}
```

## Jak powstał

- Nauczyciel: Basal omni 1.0 max (otwarty model). Mały model uczy się jego werdyktów (destylacja).
- Uczeń: TF-IDF i regresja logistyczna, która odróżnia oszustwo od każdej innej reklamy. Usługa uczy go przy starcie z pliku `dane/reklamy.jsonl` (kilka sekund), więc w repo nie ma pliku modelu.
- Przed liczeniem tekst jest sprowadzany do zwykłej pisowni (`tekst.py`, `normalizuj`): litery ozdobne z Unicode (na przykład pogrubione), litery z cyrylicy i greki udające łacińskie, niewidoczne znaki wewnątrz słów, brak polskich znaków. Tak piszą oszuści, którzy omijają filtry słów.
- Dane: prawdziwe reklamy i strony z etykietą (Google Ads Transparency, raporty CSIRT KNF, Biblioteka reklam Meta, TikTok), reklamy syntetyczne, które napisał otwarty model Gemma 4, i zwykłe reklamy z Biblioteki reklam Meta (sklepy, fundacje, kancelarie).
- Reklamy syntetyczne służą tylko do nauki. Wszystkie wyniki niżej są liczone na prawdziwych reklamach.
- Czyszczenie tekstu (`tekst.py`, to samo przy nauce i w usłudze): wyrzuca napisy interfejsu („Sponsorowane”, „Learn More”, „Dowiedz się więcej”, numer z Biblioteki reklam) i nazwę strony nad postem. Bez tego model zgadywał po przyciskach, z jakiego źródła jest reklama.
- Tekst 143 reklam pochodzi z obrazków. W usłudze tekst da OCR (PP-OCR), sprawdzone na 57 reklamach: 3 z 57 werdyktów się zmieniają.
- Testy: `docker compose run --rm ai python test_przewidz.py` i `docker compose run --rm ai python test_main.py`
- Wersje: scikit-learn 1.9.1, Python 3.11.

## Wyniki

Liczone na prawdziwych reklamach i stronach, których model nie widział przy nauce (5 podziałów × 5 losowań, średnia), względem etykiet: ręcznych, a dla 197 reklam firm z rejestru nadanych z płatnika.
Teksty z tej samej kampanii, szablonu, strony na Facebooku albo jednego płatnika trafiają razem do nauki albo razem do testu, a prawie identyczne oszustwa (co najmniej połowa wspólnych trójek znaków) też. Reklamy syntetyczne i zwykłe reklamy z Biblioteki reklam Meta są tylko w nauce.

W zestawie jest 95 oszustw i 374 prawdziwe reklamy inwestycyjne, które nie są oszustwem (w tym 197 reklam firm z rejestru). Model poprzedni (wersja 4, uczony na 865 tekstach bez nowych danych) i obecny są liczone na tych samych podziałach.

| Próg ryzyka | Poprzedni: złapane z 95 / fałszywe alarmy z 374 | Obecny: złapane z 95 / fałszywe alarmy z 374 |
|---|---|---|
| 0,3 | 80,4 / 9,2 | 90,4 / 8,0 |
| 0,4 | 72,6 / 4,2 | 87,2 / 3,6 |
| 0,5 | 66,4 / 1,6 | 82,4 / 1,8 |
| 0,6 | 62,8 / 1,0 | 79,0 / 1,2 |
| 0,7 | 55,8 / 0,0 | 74,4 / 0,0 |

Przy tych samych fałszywych alarmach obecny model łapie o 10 do 19 oszustw więcej. Pełna tabela dla suwaka czułości w panelu: `progi.csv`.

Kolejność w kolejce (AUC: 1,0 znaczy, że każde oszustwo stoi wyżej niż każda inna reklama, 0,5 to rzut monetą): poprzedni 0,974, obecny 0,982. Średnia precyzja (AP, ważniejsza przy niewielu oszustwach): 0,945 i 0,973. Kontrola z pomieszanymi etykietami w całej nauce: AUC 0,52.

Test w sejfie: 34 z 65 nowych oszustw z CSIRT odłożono, zanim wybraliśmy ustawienia modelu, i oceniono je raz, na końcu. Model poprzedni łapie z nich 30 od progu 0,3 i 25 od progu 0,7 (tak samo działająca usługa, przez OCR i `/ocen`), obecny 32 i 29. Te liczby dotyczą modelu uczonego bez sejfu; model w usłudze uczy się już także na nim.

Odporność na sztuczki z pisownią: te same 34 oszustwa z sejfu, tekst zmieniony przed oceną, złapane od progu 0,3 / 0,7.

| Zmiana tekstu | Poprzedni | Obecny |
|---|---|---|
| bez zmian | 30 / 25 | 32 / 29 |
| litery pogrubione z Unicode | 5 / 0 | 32 / 29 |
| litery z cyrylicy zamiast łacińskich | 5 / 0 | 32 / 29 |
| niewidoczne znaki w słowach | 18 / 0 | 32 / 29 |
| bez polskich znaków | 30 / 23 | 32 / 29 |
| błędy OCR w 8 % liter | 30 / 22 | 32 / 27 |

Werdykt wynika z samego ryzyka oszustwa: poniżej 0,3 `ok`, od 0,7 `oszustwo`, pomiędzy albo bez tekstu `do_sprawdzenia` (wtedy `pewny` jest fałszem). Według tabeli wyżej: od 0,7 model wskazuje 74,4 z 95 oszustw bez fałszywego alarmu, a od 0,3 do człowieka trafia 90,4 z 95 przy 8 fałszywych alarmach na 374. Model uczy się tylko dwóch klas, oszustwo albo nie. Czy uczciwej reklamie brokera czegoś brakuje, sprawdzają reguły modułów M1–M3. Kolejkę w panelu ustawia próg ryzyka. Opisów filmów (źródło `youtube`) model nie ocenia: był uczony i mierzony na reklamach, a na opisach filmów edukacyjnych dawał fałszywe alarmy. Dla filmów działają reguły modułów.

Próby dodatkowe:

- Model uczony bez ani jednego prawdziwego oszustwa (same syntetyczne) złapał 15,8 z 30 prawdziwych oszustw przy 0 fałszywych alarmach na 177.
- 298 zwykłych reklam z Meta podzielone stronami na dwie połowy, każdą ocenia model uczony bez niej. Od progu 0,3: 17 (poprzedni 15), od 0,5: 6 (poprzedni 1), od 0,7: 0 (poprzedni 0). To głównie pożyczki unijne BGK („inwestycje”), kancelarie od zwrotu kosztów kredytu („odzyskaj”) i promocje („zyskaj”).
- 579 rekordów w bazie pokazowej (bez filmów), ocenione obecnym modelem: żaden nie dostał nowego werdyktu `oszustwo`, 2 reklamy Google przeszły z `do_sprawdzenia` na `ok`, jedna strona z grupą na Discordzie z `ok` na `do_sprawdzenia` (ryzyko 0,33).
- 12 stron firm z listy ostrzeżeń KNF, które dalej mają ofertę: model w wersji 4 wskazał 0 z 12, obecnego nie mierzono. Patrz ograniczenia.

## Świeży test

Sprawdzony po wyborze modelu na tekstach, których nie było w nauce ani w porównaniach wariantów: podobieństwo do każdego z nich poniżej 0,5 (wspólne kawałki po 5 znaków). Obok ocena Basal omni na tym samym tekście.

| Zestaw | Ile | KAPSEL od 0,3 / 0,5 / 0,7 | Basal od 0,3 / 0,5 / 0,7 |
| --- | --- | --- | --- |
| Zwykłe reklamy z Google, TikToka i Meta z bazy pokazowej, oznaczone bez patrzenia na oceny (fałszywe alarmy) | 153 | 0 / 0 / 0 | 2 / 1 / 0 |
| Opublikowane zrzuty reklam-oszustw z ostrzeżeń CERT Polska i CSIRT KNF oraz z artykułów Antyweb i CyberDefence24, tekst odczytany usługą `odczyt` (wykryte) | 6 | 6 / 5 / 5 | 6 / 6 / 6 |
| Zrzuty stron-oszustw z tych samych ostrzeżeń (wykryte) | 5 | 5 / 5 / 5 | 5 / 5 / 5 |
| Kolejne zrzuty reklam-oszustw z CERT Polska, CSIRT KNF, Demagog i Antyweb, zebrane po pierwszym świeżym teście (wykryte) | 13 | 13 / 10 / 9 | nie oceniano |

- W pierwszej szóstce jedyna reklama-oszustwo poniżej 0,7 (0,46) to film z PGNiG, w którym prawie cały tekst jest po angielsku. W kolejnych 13 poniżej 0,7 są dwie reklamy-przynęty ze znaną osobą bez słowa o pieniądzach (0,42 i 0,45), reklama „strona tylko dla 100 osób” (0,43) i zlepek zrzutów fałszywego konta bankowego (0,55): wszystkie trafiają do sprawdzenia przez człowieka.
- 5 reklam z bazy, w których oszustwo widać po płatniku i domenie, a nie po słowach (konto z nazwą Interactive Brokers płaci za reklamy Quotex i dwóch innych platform; obligacje skarbowe od estońskiej spółki z nieznaną domeną): oba modele dają poniżej 0,3, bo tekst jest neutralny. Każda z 5 dostaje poziom wysoki z reguł api (`obca_domena`, `platnik_poza_listami`).
- 53 reklamy, których nie da się ocenić z samego tekstu (pusty tekst, sama nazwa marki, „best online broker”), nie weszły do tabeli; KAPSEL żadnej z nich nie dał od 0,3.
- 24 oszustwa to mała próbka: pokazuje kierunek, nie procent.

## Co jeszcze potrafi

- Powody: do 5 słów, które najmocniej podniosły ryzyko. Usługa wyjmuje słowo z tekstu w każdej pisowni („ZARABIAJ”, „zarabiaj!”, „zarabiac”) i sprawdza, o ile spada ocena. Liczby, adresy stron, słowa krótsze niż 3 litery, spójniki, zaimki i etykiety formularzy („imię”, „e-mail”) nie są powodami. Słowa są w polu `powody` każdej reklamy. Powodów szuka tylko przy ryzyku od 0,1 w górę: to jedno przewidywanie na słowo, a przy niższym ryzyku nie ma czego tłumaczyć.
- Rodzaj oszustwa: drugi mały model tego samego typu. Zna 4 rodzaje: podszycie pod markę, osobę lub urząd; obietnica gwarantowanego zysku; zamknięta grupa z sygnałami; odzyskiwanie straconych pieniędzy. Uczy się na syntetycznych oszustwach i na wszystkich reklamach, które nie są oszustwem, żeby umiał nie podać żadnego rodzaju. Rodzaje są szerokie, bo przy drobnych ogólna obietnica zysku dostaje przypadkową nazwę. Rodzaj jest podawany tylko przy ryzyku od 0,3 i pewności rodzaju od 0,5, inaczej pole jest puste.
  - Syntetyczne oszustwa pisane innym stylem niż te z nauki: rodzaj pojawia się przy 127 z 200 i jest trafny w 122.
  - 32 prawdziwe oszustwa, rodzaj opisany ręcznie przed pomiarem: pojawia się przy 10, w żadnym nie jest błędny.
  - 633 reklamy, które nie są oszustwem, oceniane przez model uczony bez nich: żadna nie dostała rodzaju.
- Nauka z decyzji analityka: oceny `ok` i `oszustwo` wpisane w panelu trafiają do nauki (`POST /ucz`). „Wymaga sprawdzenia” nie trafia, bo to jeszcze nie werdykt. Model uczy się od nowa w kilka sekund i wszystkie reklamy w bazie dostają nową ocenę. Tabela w `progi.csv` opisuje model bez tych dopisków.
Reguły modułów M2 i M3 (`wymogi.py`, `doradztwo.py`). To wyrażenia na tekście, nie model. M2 działa tylko dla płatnika z rejestrów KNF i sprawdza w tekście kryteria UKNF: obietnicę zysku bez informacji o ryzyku (3), informację o ryzyku w innym języku niż reklama (10), wyniki z przeszłości bez okresu pięciu lat i źródła (12a), bez wpływu opłat albo kursu walut (12b) i bez zastrzeżenia (14), porównanie oferty bez źródła, rankingu ani daty (11), prognozę z liczbą bez zastrzeżenia (15), ulgi podatkowe bez zastrzeżenia (16) oraz nadzór użyty jako argument bezpieczeństwa albo aprobaty (17, 18). Do tego reklamę CFD albo forex bez standardowego ostrzeżenia o odsetku rachunków ze stratą. Numer kryterium UKNF stoi w podstawie każdego ustalenia. M3 działa tylko dla płatnika spoza list albo nieznanego i szuka oferty doradztwa inwestycyjnego, zarządzania majątkiem i family office (`doradztwo_bez_zezwolenia`). Sygnały i rekomendacje rozsyłane ogółowi to osobne ustalenie średniego poziomu (`rekomendacje_ogolne`), bo zezwolenia wymaga dopiero rada dla konkretnej osoby. Fraza poprzedzona zaprzeczeniem („nie stanowi rekomendacji”, „to nie jest doradztwo inwestycyjne”) nie daje ustalenia. Reguł o wyglądzie reklamy (wielkość czcionki, kontrast, jedno kliknięcie) tu nie ma, bo tekst ich nie pokazuje. M3 wymaga też słowa oferty obok frazy („oferujemy”, „dołącz”, „pobierz”) i pomija menu strony oraz teksty kancelarii prawnych. Reguła o zysku nie działa dla kont, lokat i odsetek, bo te przepisy ich nie obejmują. Ustalenie o rejestrze (M1) dostaje tylko reklama, która mówi o inwestowaniu, albo marka znana z rejestru pod inną spółką (`temat.py`): giełda odpadów, pośrednik nieruchomości i reklama z samym logo go nie dostają. Płatnik spoza list KNF, który jest w rejestrze MiCA (ESMA, dostawcy usług w zakresie kryptoaktywów z licencją innego państwa UE, plik `rejestr_mica.csv`), nie dostaje ustalenia M1; inna spółka marki z tego rejestru daje ustalenie jak przy marce z rejestru KNF. Ustalenia M1 nie dostaje też emitent produktu notowanego na giełdzie (ETP), bo sprzedaje go przez domy maklerskie, ani firma z rachunkiem symulowanym, który nie angażuje pieniędzy klienta. Na 1775 rekordach w bazie M3 dało 4 ustalenia (wszystkie o sygnałach), M2 w tekście dziesięć (CFD bez ostrzeżenia 4, podatki 4, wyniki z przeszłości bez zastrzeżenia 1, porównanie bez podstawy 1), M1 141 (91 płatników spoza rejestru przy marce z list, 50 spoza list). Ustalenia M2 i M3 przeczytaliśmy wszystkie; dwa ustalenia M2 są słabe.

Wektor reklamy (`osadzenia.py`). Każdy tekst dostaje 64 liczby: TF-IDF na ciągach znaków, zmniejszone rozkładem SVD (LSA). To nie jest sieć neuronowa. Wektor służy do szukania podobnych reklam i powtórek tej samej reklamy przez cosinus. Przestrzeń jest dopasowana raz, na pliku `dane/reklamy.jsonl`, i nie zmienia się, gdy klasyfikator uczy się od analityków, więc stare i nowe wektory da się porównywać, a wektor reklamy liczy się raz (`POST /osadz`). Zmierzone na 200 zebranych reklamach: ta sama reklama z podmienioną co dziesiątą częścią słów ma cosinus 0,997 (mediana) i 0,984 (5. percentyl), dwie losowe reklamy 0,56 (mediana) i 0,87 (95. percentyl). Tekst na 600 słów liczy się około 19 ms na procesorze. Na 143 opisanych reklamach (73 pary z tej samej kampanii lub szablonu, 10 080 pozostałych) cosinus rozdziela pary tak samo jak podobieństwo trigramów: AUC 0,891 wobec 0,889. Przy progu 0,97 łapie 4 pary z jednej grupy i 21 spoza niej. Dlatego podobne reklamy panel nadal wyszukuje trigramami, a wektor jest dostępny pod `POST /osadz` i niczego nie rozstrzyga sam.

## Ograniczenia

- Prawie wszystkie z 95 prawdziwych oszustw pochodzą z raportów CSIRT KNF: posty, reklamy i fałszywe strony, głównie „szybki zysk pod znaną marką” (Orlen, PGE, NVIDIA, CD Projekt), kryptowaluty i fałszywe artykuły. Oszustwa z innych źródeł i nowsze schematy model zna tylko z reklam syntetycznych. W sejfie przeoczył fałszywy artykuł o inflacji podpisany „money.pl” i reklamę akcji Airbnb: w tekście nie ma obietnicy zysku.
- Nie łapie firm bez licencji, które wyglądają jak zwykły broker. Na 12 stronach z listy ostrzeżeń KNF nie wskazał żadnej. Tu rozstrzyga rejestr, nie tekst.
- Zwykłe reklamy z Biblioteki reklam Meta nie były oglądane pojedynczo. Przyjęto, że nie ma wśród nich oszustw inwestycyjnych.
- Oszustwa z Facebooka mają w tekście także napisy z obrazka („900 zł”, „dostaniesz”), bo pochodzą ze zrzutów ekranu. Uczciwe reklamy z Meta mają tylko tekst posta. Część różnicy może brać się z tego, nie z treści. Do sprawdzenia po OCR obrazków z Meta.
- Wśród samych reklam Google (3 oszustwa na 116) model zgaduje słabo (1 z 3). Dwa z nich to reklamy wykupione przez osobę prywatną pod cudzą marką: z tekstu nie do wykrycia, wykrywa je sprawdzenie, kto płaci.
- Etykiety reklam z Meta są ręczne i tylko z tekstu posta. Ostrzeżenie mogło być na obrazku.
- Reklama wideo jest oceniana po tekście posta i tekście z jednej zapisanej klatki. Mowę model czyta tylko z nagrania dodanego do reklamy (usługa `odczyt`, model Whisper). Model uczył się na polskich tekstach: oszustwo po angielsku, w tekście albo w mowie, dostaje niskie ryzyko. Mowa nigdy nie obniża ryzyka samego tekstu posta.
- 95 oszustw to wciąż mało. Wyniki mają rozrzut kilku punktów procentowych.
- 197 reklam firm z rejestru jest w nauce, więc ich ocena w bazie pokazowej jest liczona na tekstach, które model zna. Tak samo 32 oszustwa z CSIRT w bazie pokazowej.

## Co poprawi model

1. Prawdziwe oszustwa innych rodzajów i z innego źródła niż raporty CSIRT (w zapisach z Biblioteki reklam Meta nie było ani jednego).
2. Cecha „płatnik albo firma jest na liście KNF”.
3. OCR obrazków reklam z Meta, żeby obie grupy miały tekst tego samego rodzaju.
4. Więcej werdyktów nauczyciela na 350 reklamach z modułu 2.
