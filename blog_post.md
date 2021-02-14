Jeśli nie interesują Cię założenia i proces zbierania danych - przejdź sobie dalej, do **[omówienia zebranych informacji](#analiza)**. Ale nie narzekaj wówczas na założenia omówione poniżej.

# Żródło danych oraz wstępne założenia

Źródłem danych do dzisiejszego wpisu jest strona [SpotifyCharts.com](https://SpotifyCharts.com) na której znajdują się listy 200 najpopularniejszych utworów odtwarzanych każdego dnia (lub tygodnia) w Spotify. A na *drugą nogę* wykorzystane zostało API Spotify (na potrzeby zgomadzenia szczegółowych informacji o utworach).

**Uwaga:** nie mamy wyjaśnienia co oznacza liczba odtworzeń (czy jest to guzik Play na utworze i od razu Stop? a może utwór musi być przesłuchany w 100%? a może tylko w 50%?) - Spotify pisze tylko w swoim [FAQ](https://artists.spotify.com/faq/stats#charts), że *These figures are generated using a formula that protects against any artificial inflation of chart positions* co niczego nie wyjaśnia.

Abstrahując od tego co oznacza liczba "streams" przyjmujemy że jest ona dobrym wskaźnikiem popularności danego utworu w określonym czasie (dzień lub tydzień) oraz miejscu (globalnie lub konkretnym kraju).

Właśnie - kraju. To jest najciekawsze w tych sstatystykach - mamy podział na poszczególne państwa w których obecny jest Spotify. I znowu: czy przesłuchanie utworu zalicza się do państwa A czy B ze względu na wskazany przez użytkownika w profilu kraj pochodzenia/zamieszkania czy też lokalizację urządzenia (rozpoznaną według adresu IP) na którym utwór był odtwarzany? Może to marginalne, ale warto o tym wspomnieć. Czy Polak w Londynie słucha bardziej *polskiej* czy *londyńskiej* muzyki? Nie wiemy.

I ostatni *disclaimer* do poniższych statystyk - dane dotyczą oczywiście użytkowników aplikacji Spotify. Nie wiemy jak wyglądają wyniki słuchalności dla całej populacji danego kraju. Nie wiemy (zapewne nie) czy można uogólnić wnioski na wszystkich mieszkańców danego kraju. Kilka liczb za [Spotify Usage and Revenue Statistics (2020)](https://www.businessofapps.com/data/spotify-statistics/), które dają jakiś obraz założeń:

* Spotify’s can lay claim to **36% of the global streaming market**
* (...) we see that Spotify has the most youthful user base (...), **with over half of users aged 34 or under**
* Average hours spent listening to Spotify per month stands at 25 hours
* 44% of users listen to Spotify on a daily basis
* Average users listen to 41 unique artists per week
* według [opracowania](https://www.visualcapitalist.com/how-many-music-streams-to-earn-a-dollar/) stawka za odsłuchanie to 0.437 centa i taką przymiemy do dalszych obliczeń (70% trafia do wydawcy, reszta to artysty)
* liczba użytkowników Spotify w kolejnych kwartałach na podstawie [strony](https://www.businessofapps.com/data/spotify-statistics/#1) oraz raportów finansowych spółki 


# Pobranie danych

Żeby nie zwariować od nadmiaru danych użyłem zestawień tygodniowych. Repozytorium z kodem źródłowym znajdziecie na [moim GitHubie](https://github.com/prokulski/SpotifyCharts). W skrócie proces wygląda następująco:

* wchodzimy na stronę główną (w wersji *notowania tygodniowe*)
* pobieramy listę dostępnych krajów
* dla kazdego z tych krajów:
   * wchodzimy na stronę główną kraju (też notowań tygodniowych)
   * pobieramy listę dostępnych dat (kolejnych tygodni)
   * dla każdej z daty - pobieramy plik CSV (to jest zbawienie, nie trzeba za bardzo scrappować) z zestawieniem

W plikach z notowaniami mamy między innymi ID utowru w bazie Spotify. Na tej podstawie szukamy informacji szczegółowych o utworze - tzw. *audio features* (cechy opisane są w [dokumentacji API](https://developer.spotify.com/documentation/web-api/reference/#object-audiofeaturesobject)) oraz informacji o artyście (gatunki jakie reprezentuje). To powinno wystarczyć na nasze potrzeby.

Cały proces przygotowany jest (mam nadzieję) zgrabnie i na przykład nie są pobierane wielokrotnie te same informacje o wykonawcy czy albumie.

W szczegółach wygląda to tak, że każde notowanie jest zapisywane jako oddzielny plik CSV, a każda informacja o artyście czy utworze to oddzielne pliki JSON. Na podstawie nazwy plików można niektóre pominąć, a co za tym idzie - odpalić proces zbierania danych w dowolnym momencie dociągając tylko braki albo nowe dane.

Z dużej ilości plików CSV i (nieco mniejszej ilości) plików JSON budowane są przy użyciu PySparka zbiory w formacie Parquet. Dzięki temu w samej analizie działamy szybciej oraz nie potrzebujemy tak dużo pamięci. Kiedyś podobny sposób zastosowałem [korzystając ze Sparka w R](/index.php/2018/12/21/spark-czyli-opoznienia-pociagow/), dzisiaj będzie w Pythonie.

Dla przejrzystości tym razem wpis bez kodu źródłowego (treści jest tyle, że nie warto jej dodatkowo gmatwać). Wszystko znajdziesz na [moim GitHubie](https://github.com/prokulski/SpotifyCharts) (o ile Cię to w ogóle interesuje).


# Analiza

## Ogólny przegląd

* ile streamów łącznie tydzień po tygodniu

* rozbicie na kontynenty

* najpopularniejsi wykonawcy
  * wg streamów total
    * top globalnie
    * top na kontynencie
  * wg ilości razy na top1
    * top globalnie
    * top na kontynencie
   
* popularność gatunków (wg streamów)
  * najpopularniejsze gatunki (agregaty) - na totalu
  * jak zmieniała się popularność gatunków? (procenty)
  * to samo dla Polski

* liczba streamów w zależności od pozycji

* rok wydania utworu a liczba streamów (czy słucha się nowych czy wszystkiego)
  * lata 2017-2021, każda linia osobno
  * lata 2010-2017 - linia dodatkowa
  * potem dekadami kolejne linie

### Polska vs reszta świata

* top wykonawców w Polsce
  * zmiana w czasie

* ilu z top światowego jest w top polski?

* premiery polskich hitów (Podsiadło, Taco)

## Cechy audio

* średnia ważona cech dla kraju po tygodniach

* popularity vs inne audio features

### Podobieństwo państw na pdstawie cech

* uśredniony wektor cech dla państwa - globalnie

* usredniony wekrot cech dla państwa po tygodniach i jego odległość kosinusowa z innymi krajami w danym tygodniu

* jak zmieniała się taka odległość między państwami (czy kraje się od siebie zbliżają albo oddalają?)

* odległość krajów od siebie - odległość środków państw a odległość kosinusowa po cechach 

### Gatunek a cechy audio

* boxplot per gatunek (z top najpipularniejszych + ręcznie wybrane)

## Top Wszech Czasów

* punktacja za miejsce na liście (1 miejsce = 200 pkt, 200 miejsce = 1 pkt)
  * globalnie
  * US, UK, PL

## Wejście do top5

* ile czasu zajmuje od premiery do pojawienia się w top200?

* w szczególności dla piosenek z pierwszego miejsca
 * czy to się różni US / UK vs PL?
 * pierwszy moment pojawienia się w top - jak długo czasu i na które miejsce?

* ile % streamów zgrania top1? ole top3?

* popularity pioseniki vs łączna liczba streamów

## Boże Narodzenie

* jacy artyści są popularni?

* kiedy zaczyna się granie "Last Christmas" i innych podobnych piosenek?

## Kasa
* Ile kasy zgadnie artysta?
  * według [opracowania](https://www.visualcapitalist.com/how-many-music-streams-to-earn-a-dollar/) stawka za odsłuchanie to 0.00437 dolara i taką przymiemy do dalszych obliczeń

# PowerBI
