#Dashboard:

- [FEATURE] Główny dashboard aplikacji
  Opis: Zbudowanie globalnego dashboardu aplikacji prezentującego najważniejsze agregaty systemu (np. koszty, kontrakty, kontrahenci, ostatnie faktury itp.). 
  Priorytet: Niski – realizacja dopiero pod koniec, gdy większość funkcjonalności domenowych będzie już gotowa.

#Kontrakty:

- [FEATURE] Filtrowanie listy kontraktów
  Obszar: Contracts

  Opis:
  Na widoku listy kontraktów dodać możliwość filtrowania kontraktów według stanu.

  Podstawowe filtry:
  - status kontraktu (np. active, planned, cancelled, finished)
  
  Możliwe rozszerzenia:
  - filtrowanie po kontrahencie
  - filtrowanie po dacie rozpoczęcia / zakończenia
  - filtrowanie po typie kontraktu
  - szybkie przełączniki (np. tylko aktywne)

  Cel:
  Ułatwienie pracy na większej liczbie kontraktów i szybsze odnajdywanie interesujących rekordów.

- [FEATURE] Lista faktur z zakresu w drzewie kosztów kontraktu
  Obszar: Contracts / Contract Details

  Opis:
  W widoku szczegółów kontraktu (drzewo kosztów) dodać przy każdej linii drzewa przycisk **"Faktury"**, który pozwoli wyświetlić listę faktur należących do danego zakresu.

  Aktualne zachowanie (zostaje):
  - kliknięcie w całą linię drzewa otwiera modal
  - modal pokazuje podział kosztów według typu (np. materiał, robocizna)

  Nowe zachowanie:
  - w modalu, przy liniach kosztów (np. materiał / robocizna), kliknięcie w linię powinno otworzyć **listę faktur należących do tego zakresu**

  Cel:
  Umożliwienie szybkiego przejścia:
  agregat kosztów → typ kosztu → konkretne faktury źródłowe.

- [FEATURE] Tworzenie drzewa kontraktu z kosztorysu (LLM import)
  Obszar: Contracts / Contract Creation

  Opis:
  Podczas tworzenia nowego kontraktu dodać możliwość utworzenia **struktury drzewa kosztów na podstawie zewnętrznego kosztorysu**.

  Flow:
  1. Użytkownik przesyła plik kosztorysu (np. PDF / DOC / XLS / TXT).
  2. Plik jest wysyłany do LLM w celu analizy struktury kosztorysu.
  3. LLM zwraca ustrukturyzowany **JSON drzewa kosztów**.
  4. System na podstawie JSON tworzy **strukturę drzewa kontraktu** w domenie.

  Dodatkowo:
  - oryginalny plik kosztorysu jest zapisywany w systemie jako **document powiązany z kontraktem**
  - dokument jest dostępny później do wglądu z poziomu kontraktu

  Cel:
  Przyspieszenie tworzenia kontraktów oraz automatyczne budowanie struktury kosztów na podstawie istniejących kosztorysów.

#Własne firmy:

- [FEATURE] Rozszerzenie dashboardu finansowego firm własnych
  Obszar: Company Finance Dashboard

  Opis:
  Dashboard finansowy pokazuje obecnie zestawienie wyników finansowych dla:
  - bieżącego roku
  - bieżącego miesiąca
  - poprzednich miesięcy
  - historii z poprzednich lat

  Aktualne zachowanie:
  - kliknięcie w linię okresu otwiera modal
  - modal pokazuje podział kosztów według typu

  Nowe funkcjonalności:

  1. **Drill-down do faktur z poziomu typu kosztu**
     - kliknięcie w dany typ kosztu w modalu powinno otworzyć **listę faktur należących do tego zakresu i typu kosztu**

  2. **Rozszerzone filtrowanie listy faktur**
     Lista faktur otwierana z dashboardu jest obecnie statyczna (fixed).  
     Należy dodać możliwość dodatkowego filtrowania:

     - po kliencie (nazwa)
     - po NIP klienta
     - po tytule faktury
     - po kontrakcie, którego dotyczy faktura

  Cel:
  Umożliwienie przejścia z poziomu agregatów finansowych do konkretnych dokumentów źródłowych oraz łatwiejsze przeszukiwanie faktur w danym okresie.

- [IMPROVEMENT] Zarządzanie firmami własnymi z poziomu dashboardu finansowego
  Obszar: Company Finance Dashboard / Own Companies

  Opis:
  Uporządkowanie zarządzania firmami własnymi poprzez przeniesienie funkcji do dashboardu finansowego.

  Zmiany:

  1. **Przeniesienie przycisku tworzenia firmy**
     - przenieść przycisk **"Nowa firma własna"** z sekcji *Kontrahenci* do **Dashboardu firm własnych**

  2. **Podgląd danych firmy własnej**
     - dodać przycisk **"Dane firmy"**
     - kliknięcie otwiera **modal z metadanymi firmy**

  3. **Edycja danych firmy**
     - w modalu z danymi firmy dodać przycisk **"Edytuj"**
     - przejście do formularza edycji danych firmy

  Cel:
  Lepsza organizacja systemu – firmy własne są elementem finansów systemu, a nie klasycznymi kontrahentami.

- [FEATURE] Sekcja "Aktualny stan" na dashboardzie firm własnych
  Obszar: Company Finance Dashboard / Own Companies

  Opis:
  Na ekranie dashboardu firm własnych dodać sekcję prezentującą **aktualny stan finansowy i operacyjny** firmy.

  Początkowa funkcjonalność:
  - **nadchodzące płatności** (np. faktury do zapłaty w najbliższym okresie)

  Możliwe przyszłe rozszerzenia:
  - zaległe płatności (przeterminowane faktury)
  - faktury wystawione, ale jeszcze nieopłacone
  - szybkie podsumowanie kosztów bieżącego miesiąca
  - ostatnio dodane faktury
  - szybkie alerty finansowe

  Cel:
  Zapewnienie szybkiego wglądu w bieżącą sytuację finansową firmy bez konieczności przeglądania szczegółowych raportów.

- [FEATURE] System płatności cyklicznych dla firm własnych
  Obszar: Company Finance Dashboard / Own Companies

  Opis:
  Wprowadzenie systemu obsługi **cyklicznych zobowiązań finansowych** dla firm własnych.

  Przykłady:
  - ZUS
  - księgowość
  - kredyty
  - leasing
  - abonamenty
  - inne stałe koszty

  Funkcjonalność:

  1. **Definicja płatności cyklicznej**
     Możliwość zdefiniowania:
     - nazwy zobowiązania
     - firmy własnej
     - częstotliwości (np. miesięcznie)
     - dnia pojawienia się wpisu w systemie
     - terminu płatności
     - domyślnej kwoty

  2. **Typ kwoty**
     - **stała kwota**
     - **zmienna kwota**

  3. **Automatyczne tworzenie wpisów**
     System generuje wpisy finansowe według harmonogramu.

  4. **Automatyczne zatwierdzanie**
     - jeśli kwota jest **stała** → wpis może być **automatycznie zatwierdzony**
     - jeśli kwota jest **zmienna** → wymaga potwierdzenia / uzupełnienia kwoty

  Cel:
  Automatyzacja powtarzalnych kosztów i lepsza kontrola nad zobowiązaniami finansowymi firmy.

#Kontrahenci:

- [IMPROVEMENT] Automatyczne czyszczenie nieużywanych kontrahentów
  Obszar: Counterparties

  Opis:
  Dodać worker uruchamiany przy starcie systemu, który usuwa kontrahentów niepowiązanych z żadnymi danymi w systemie.

  Kryterium usunięcia:
  - kontrahent nie posiada żadnych powiązań z:
    - kontraktami
    - fakturami
    - innymi wpisami systemowymi

  Działanie:
  - worker uruchamiany przy **starcie aplikacji**
  - wyszukuje kontrahentów bez powiązań
  - usuwa ich poprzez **delete**

  Cel:
  Utrzymanie czystości danych i eliminacja pustych rekordów kontrahentów w systemie.

- [IMPROVEMENT] Obsługa firm własnych w liście kontrahentów
  Obszar: Counterparties

  Opis:
  Rozważano usunięcie firm własnych z listy kontrahentów poprzez filtrowanie.

  Aktualna decyzja:
  **Firmy własne pozostają w tabeli kontrahentów**, ponieważ są wykorzystywane w różnych miejscach systemu (np. picker w modalach).

  Możliwe przyszłe ulepszenie:
  - oznaczenie kontrahenta typem:
    - `OWN_COMPANY`
    - `COUNTERPARTY`
  - możliwość filtrowania po typie na liście kontrahentów

  Cel:
  Zachowanie spójności danych i uniknięcie problemów z wyborem podmiotów w pickerach formularzy.

- [FEATURE] Statystyki i sortowanie na liście kontrahentów
  Obszar: Counterparties

  Opis:
  Rozszerzenie widoku listy kontrahentów o podstawowe statystyki oraz możliwość sortowania rekordów.

  Nowe elementy:

  1. **Liczba faktur**
     - dodać kolumnę **"Liczba faktur"**
     - pokazuje ile faktur jest powiązanych z danym kontrahentem
     - pozwala szybko ocenić skalę współpracy z danym podmiotem

  2. **Sortowanie listy**
     Możliwość sortowania kontrahentów według:

     - liczby faktur
     - nazwy kontrahenta
     - daty ostatniej faktury

  Cel:
  Szybka identyfikacja najaktywniejszych kontrahentów oraz łatwiejsza nawigacja po liście.

- [FEATURE] Filtrowanie listy faktur w szczegółach kontrahenta
  Obszar: Counterparties / Counterparty Details

  Opis:
  W widoku szczegółów kontrahenta rozszerzyć listę faktur o możliwość filtrowania, analogicznie jak w widoku faktur dla firm własnych.

  Dostępne filtry:

  - **numer faktury**
  - **zakres kwot** (od – do)
  - **kontrakt**, którego dotyczy faktura

  Cel:
  Ułatwienie analizy faktur powiązanych z danym kontrahentem oraz szybsze odnajdywanie konkretnych dokumentów.

#Umowy(Agreements):

- [FEATURE] Moduł umów z kontrahentami
  Obszar: Counterparties / Agreements

  Opis:
  Dodanie modułu zarządzania **umowami z kontrahentami** dostępnego z poziomu widoku kontrahenta.

  Funkcjonalność:

  1. **Lista umów**
     - w szczegółach kontrahenta dodać sekcję **"Umowy"**
     - lista wszystkich umów powiązanych z danym kontrahentem

  2. **Podgląd umowy**
     - możliwość otwarcia szczegółów umowy

  3. **Tworzenie nowej umowy**
     - formularz tworzenia nowej umowy

  4. **Edycja umowy**
     - możliwość modyfikacji danych umowy

  Architektura:

  - umowy są **strukturalnie takie same jak kontrakty**
  - różnią się jedynie **typem (Agreement vs Contract)**

  W praktyce:
  - większość logiki domenowej już istnieje
  - potrzebny będzie:
    - osobny **service**
    - lekkie modyfikacje **widoków**

  Cel:
  Zarządzanie formalnymi umowami z kontrahentami oraz powiązanie ich z kontraktami i fakturami w systemie.

#Dokumenty:

- [FEATURE] Rozszerzenie zarządzania dokumentami
  Obszar: Documents

  Opis:
  Rozbudowa funkcjonalności listy dokumentów o dodatkowe filtrowanie oraz możliwość zmiany przypisania dokumentu.

  1. **Filtrowanie po czasie**
     Oprócz obecnego filtrowania po statusie (`ready`, `failed` itp.) dodać możliwość przeglądania dokumentów:

     - według **roku**
     - według **miesiąca**

     Cel:
     łatwiejsze odnajdywanie dokumentów w większych zbiorach danych.

  2. **Edycja przypisania dokumentu**
     Obecnie:
     - nowy dokument można przypisać do rekordu
     - przypisanego dokumentu **nie można zmienić ani odczepić**

     Do dodania:
     - możliwość **odpięcia dokumentu od rekordu**
     - możliwość **ponownego przypisania dokumentu** do innego rekordu

  3. **Zachowane funkcjonalności**
     - link do powiązanego rekordu
     - możliwość usunięcia dokumentu

  Cel:
  Elastyczne zarządzanie dokumentami oraz możliwość poprawiania błędnych przypisań.

- [IMPROVEMENT] Rozszerzenie automatycznego przypisywania dokumentów
  Obszar: Documents / Auto Assignment

  Opis:
  System posiada funkcję automatycznego przypisywania dokumentów do rekordów, gdy jakość rozpoznania dokumentu jest wystarczająco dobra.

  Aktualna logika dopasowania:
  - numer dokumentu
  - NIP sprzedawcy

  Problem:
  W praktyce mogą występować dokumenty powiązane z tym samym zdarzeniem gospodarczym, ale posiadające **inny numer dokumentu** (np. faktura zaliczkowa, korekta, kolejny etap rozliczenia).

  Rozszerzenie logiki dopasowania:

  System powinien wyszukiwać kandydatów do przypisania również na podstawie:

  - **NIP sprzedawcy**
  - **kwoty całkowitej dokumentu**
  - **dopasowania kwoty z przybliżeniem (tolerancja)**

  Możliwy algorytm:
  - wyszukiwanie dokumentów o tej samej kwocie lub w określonym zakresie tolerancji
  - filtrowanie po NIP sprzedawcy
  - przedstawienie kandydatów do automatycznego lub półautomatycznego przypisania

  Cel:
  Zwiększenie skuteczności automatycznego przypisywania dokumentów i obsługa przypadków takich jak:
  - faktury zaliczkowe
  - korekty
  - dokumenty o zmienionym numerze.

- [IMPROVEMENT] Ulepszenie ręcznego przypisywania dokumentów
  Obszar: Documents / Manual Assignment

  Opis:
  Obecny mechanizm ręcznego przypisywania dokumentów działa poprawnie tylko w przypadku tworzenia **nowego rekordu**.  
  Przypisanie dokumentu do **istniejącego rekordu** posiada prowizoryczny mechanizm wyszukiwania kandydatów.

  Problemy obecnej implementacji:
  - uproszczony mechanizm dopasowania
  - prymitywny dropdown z listą rekordów
  - brak wykorzystania istniejącego systemu matchingu

  Do zrobienia:

  1. **Wspólny mechanizm dopasowania**
     - wykorzystać **ten sam algorytm matchingu**, który jest używany do automatycznego przypisywania dokumentów

  2. **Lepsza lista kandydatów**
     - lista potencjalnych rekordów powinna być generowana przez mechanizm dopasowania (matching)

  3. **Zmiana UI wyboru**
     - zamiast prostego dropdowna wprowadzić **modal wyboru rekordu**
     - modal powinien prezentować kandydatów wraz z podstawowymi informacjami (np. kontrahent, kwota, data)

  Elementy, które już działają poprawnie:
  - przypisanie dokumentu do **nowego rekordu**

  Cel:
  Uspójnienie mechanizmu przypisywania dokumentów oraz poprawa ergonomii ręcznego dopasowania.

#Ksef:

- [FEATURE] Integracja z KSeF – automatyczne pobieranie faktur
  Obszar: Documents / Integrations

  Opis:
  Dodanie integracji z systemem **KSeF (Krajowy System e-Faktur)** umożliwiającej automatyczne pobieranie faktur wystawionych dla firmy.

  Funkcjonalność:

  1. **Autoryzacja w KSeF**
     - konfiguracja dostępu do KSeF dla firmy własnej
     - zapis tokenu autoryzacyjnego

  2. **Automatyczne pobieranie faktur**
     - cykliczny worker pobierający nowe faktury z KSeF
     - zapis dokumentów w module Documents

  3. **Automatyczne przetwarzanie**
     Po pobraniu faktury system może:

     - utworzyć rekord
     - spróbować dopasować kontrakt
     - dopasować kontrahenta po NIP
     - zastosować istniejący mechanizm matchingu

  4. **Powiązanie z rekordami**
     - faktura z KSeF może być:
       - automatycznie przypisana
       - lub trafić do **inboxu dokumentów**

  5. **Historia synchronizacji**
     - log pobrań z KSeF
     - informacja o błędach synchronizacji

  Cel:
  Automatyczne pobieranie faktur z KSeF bez potrzeby ręcznego uploadu dokumentów oraz integracja z istniejącym systemem przetwarzania dokumentów.

#Rekordy:


- [FEATURE] Rozszerzenie widoków w module rekordów
  Obszar: Records

  Opis:
  Główny widok rekordów posiada obecnie cztery podstawowe sekcje:

  - rekordy do przypisania
  - rekordy do wysłania do księgowej
  - niezapłacone koszty
  - niezapłacone przychody

  Brakuje jednak możliwości przeglądania rekordów, które **zostały już obsłużone**.

  Nowy widok:

  1. **Lista rekordów wysłanych do księgowej**
     - lista wszystkich rekordów oznaczonych jako wysłane do księgowej
     - widok **globalny (niezależny od firmy własnej)**

  2. **Mocne filtrowanie rekordów**
     W tym widoku powinien działać rozbudowany mechanizm filtrowania, np.:

     - firma własna
     - kontrahent
     - zakres dat
     - zakres kwot
     - kontrakt
     - typ rekordu (koszt / przychód)

  3. **Cel**
     Możliwość szybkiego odnalezienia historycznych rekordów oraz ich analizy bez konieczności przeglądania poszczególnych modułów systemu.

- [FEATURE] Widok wszystkich rekordów (globalny)
  Obszar: Records

  Opis:
  Widok prezentujący wszystkie rekordy w systemie z pełnym filtrowaniem.

  Możliwe filtry:
  - firma własna
  - kontrahent
  - kontrakt
  - zakres dat
  - zakres kwot
  - status rekordu
  - typ (koszt / przychód)

  Cel:
  Centralny punkt analizy danych finansowych systemu.

- [FEATURE] Widok rekordów wymagających uwagi
  Obszar: Records

  Opis:
  Widok agregujący rekordy, które wymagają działania użytkownika.

  Przykłady:
  - rekordy bez przypisanego kontraktu
  - rekordy bez przypisanego kontrahenta
  - rekordy z błędem przetwarzania dokumentu
  - rekordy z brakującymi danymi

  Cel:
  Szybkie wychwycenie problemów w danych systemu.

- [REFACTOR] Rozszerzenie modelu płatności rekordów (obsługa płatności częściowych)
  Obszar: Records / Payments

  Opis:
  Aktualnie rekord może zostać oznaczony jako **paid**, a data płatności zapisywana jest w momencie oznaczenia rekordu jako opłacony.  
  Model ten nie pozwala obsługiwać **częściowych płatności**.

  Zmiany w modelu danych:

  - dodać nową kolumnę **`paid_amount`**
  - pozostawić istniejące oznaczenie **paid** oraz datę płatności

  Nowa logika płatności:

  1. **Modal płatności**
     Przy oznaczaniu rekordu jako zapłacony otwiera się modal, w którym można:

     - wpisać **datę płatności**
     - wpisać **kwotę zapłaty**
     - zaznaczyć opcję **"zapłacono w całości"**

  2. **Obsługa płatności częściowych**
     - jeśli `paid_amount < total_amount` → rekord pozostaje **nie w pełni opłacony**
     - jeśli `paid_amount == total_amount` → rekord oznaczany jako **paid**

  3. **Zmiana logiki oznaczania paid przy tworzeniu rekordu**
     Obecnie:
     - `paid = true` oznacza, że faktura została opłacona

     Nowa logika:
     - przy oznaczeniu `paid = true` system powinien ustawić:
       - `paid_amount = pełna kwota faktury`

  Cel:
  Obsługa realnych scenariuszy finansowych takich jak:

  - płatności częściowe
  - płatności w ratach
  - dopłaty do faktury
  - ręczne korekty płatności.

- [FEATURE] Tworzenie kontrahenta z modala wyboru buyer/seller
  Obszar: Records / Record Form

  Opis:
  W formularzu **nowego rekordu / edycji rekordu** istnieje modal do wyboru kontrahenta (buyer / seller).  
  Obecnie można wybrać tylko kontrahentów już istniejących w systemie.

  Do dodania:

  1. **Tworzenie nowego kontrahenta z poziomu modala**
     - w modalu wyboru dodać opcję **"Dodaj nowego kontrahenta"**

  2. **Flow działania**
     - użytkownik otwiera modal wyboru buyer / seller
     - jeśli kontrahenta nie ma na liście → wybiera **"Dodaj nowego"**
     - otwiera się formularz tworzenia kontrahenta
     - po zapisaniu:
       - kontrahent zostaje zapisany
       - modal wraca do wyboru
       - nowy kontrahent jest **automatycznie wybrany**

  Cel:
  Przyspieszenie wprowadzania nowych rekordów i eliminacja konieczności przechodzenia do osobnego modułu kontrahentów.


- [IMPROVEMENT] Ujednolicenie wyboru kontraktów, nodów i typów kosztów w formularzu rekordu
  Obszar: Records / Record Form

  Opis:
  W formularzu tworzenia i edycji rekordu istnieje mechanizm przypisywania kontraktu, noda drzewa kosztów oraz typu kosztu.

  Aktualny stan:
  - **kontrakty** wybierane są z dropdownu – rozwiązanie jest wystarczające, ponieważ liczba kontraktów jest niewielka
  - **nody drzewa kosztów** oraz **typy kosztów** również używają prostych list wyboru

  Zmiany:

  1. **Modal wyboru noda drzewa kosztów**
     - zamiast prostego dropdownu wprowadzić **dedykowany modal wyboru**
     - modal powinien umożliwiać wygodne przeglądanie struktury drzewa kosztów

  2. **Możliwość tworzenia nowego noda**
     - jeśli odpowiedni node nie istnieje:
       - możliwość **utworzenia nowego noda z poziomu modala**
       - po utworzeniu node zostaje automatycznie wybrany

  3. **Ten sam pattern dla typu kosztu**
     - modal wyboru typu kosztu
     - możliwość **dodania nowego typu kosztu**, jeśli nie istnieje

  Cel:
  Uspójnienie UX formularza rekordu oraz umożliwienie tworzenia brakujących elementów bez opuszczania formularza.


- [FEATURE] Masowe przypisywanie kontraktu, noda i typu kosztu dla linii faktury
  Obszar: Records / Invoice Lines

  Opis:
  W rekordach zawierających wiele linii faktury obecnie każda linia musi być przypisywana osobno do:

  - kontraktu
  - noda drzewa kosztów
  - typu kosztu (value type)

  Jest to czasochłonne w przypadku faktur z wieloma pozycjami.

  Nowa funkcjonalność:

  1. **Masowe przypisywanie wartości**
     - możliwość ustawienia wspólnej wartości dla wszystkich linii faktury w kolumnach:
       - kontrakt
       - node
       - value type

  2. **Opcja "zastosuj dla wszystkich"**
     - w nagłówku kolumny dodać opcję:
       - **"zaznacz wszystkie"**
       - zastosowanie wybranej wartości dla wszystkich linii

  3. **Zachowanie elastyczności**
     - po masowym przypisaniu użytkownik nadal może zmienić wartość dla pojedynczej linii

  Cel:
  Znaczne przyspieszenie przypisywania danych dla faktur zawierających wiele pozycji.

- [IMPROVEMENT] Uproszczenie systemu automatycznej numeracji rekordów
  Obszar: Records / Record Form

  Opis:
  System posiada mechanizm automatycznej numeracji rekordów, jednak obecnie wymaga ręcznego wpisania wzorca numeracji w polu numeru rekordu (np. `<auto> <Y> <m>`).

  Problem:
  - rozwiązanie jest mało intuicyjne
  - użytkownik musi znać składnię numeracji

  Zmiany:

  1. **Dropdown wyboru automatycznej numeracji**
     - zamiast ręcznego wpisywania wzorca dodać **dropdown z typami numeracji**

  2. **Typy numeracji**
     W dropdownie użytkownik wybiera typ numeracji, np.:

     - numeracja miesięczna
     - numeracja roczna
     - numeracja globalna
     - numeracja według kontrahenta

  3. **Automatyczne generowanie wzorca**
     - po wyborze typu numeracji system automatycznie generuje odpowiedni wzorzec numeru

  4. **Kontekst numeracji**
     numeracja może być zależna od:

     - typu widoku (np. koszt / przychód)
     - kontrahenta

  Cel:
  Uproszczenie korzystania z automatycznej numeracji oraz eliminacja konieczności ręcznego wpisywania wzorców.

- [IMPROVEMENT] Automatyczna numeracja dla powtarzalnych wpisów
  Obszar: Records / Record Form

  Opis:
  Automatyczna numeracja rekordów ma służyć głównie do generowania numerów dla powtarzalnych wpisów (np. ZUS, księgowość, leasing), aby użytkownik nie musiał pamiętać ostatniego użytego numeru.

  Przykłady numerów:
  - `ZUS_2026_03`
  - `KSIĘGOWA_2026_03`
  - `LEASING_2026_03`

  Aktualny mechanizm:
  - użytkownik wpisuje ręcznie wzorzec, np.:
    - `ZUS_<Y>_<m>`

  Nowy mechanizm:

  1. **Dropdown wyboru automatycznej numeracji**
     - wybór typu numeracji zamiast wpisywania wzorca ręcznie

  2. **Automatyczne generowanie numeru**
     - system podstawia:
       - rok (`Y`)
       - miesiąc (`m`)
       - inne elementy wzorca

  3. **Automatyczna kontynuacja numeracji**
     - system sprawdza istniejące wpisy i generuje kolejny numer automatycznie

  Cel:
  Przyspieszenie wprowadzania cyklicznych wpisów oraz eliminacja konieczności ręcznego pilnowania numeracji.

- [FEATURE] Inteligentne przypisywanie umów do pozycji faktury
  Obszar: Records / Invoice Lines / Agreements

  Opis:
  System umożliwia przypisanie **umowy z kontrahentem** do danej pozycji faktury, gdy dana pozycja stanowi realizację tej umowy.

  Nowa logika wyświetlania i przypisywania umowy:

  1. **Sprawdzenie umów kontrahenta**
     - po wybraniu kontrahenta system sprawdza, czy istnieją powiązane **umowy z tym kontrahentem**

  2. **Brak umów**
     - jeśli kontrahent **nie posiada żadnej umowy**
     - pole przypisania umowy **nie jest wyświetlane**

  3. **Jedna umowa**
     - jeśli istnieje **jedna umowa**
     - system **automatycznie przypisuje ją do pozycji faktury**

  4. **Wiele umów**
     - jeśli istnieje **więcej niż jedna umowa**
     - pole wyboru umowy jest dostępne
     - użytkownik może ręcznie wybrać odpowiednią umowę

  5. **Wybór noda umowy**
     - przypisanie noda umowy powinno używać **tego samego modala**, który jest używany dla nodów kontraktu
     - różni się jedynie **targetem danych**

  Cel:
  Ułatwienie przypisywania pozycji faktur do realizowanych umów oraz ograniczenie zbędnych pól w formularzu.

- [IMPROVEMENT] Rozszerzenie danych kontrahenta w widoku szczegółów faktury
  Obszar: Records / Invoice Details

  Opis:
  W widoku szczegółów faktury obecnie wyświetlane są jedynie podstawowe dane stron transakcji:

  - nazwa
  - NIP

  Jest to niewystarczające przy wykonywaniu płatności lub weryfikacji danych kontrahenta.

  Zmiany:

  1. **Wyświetlanie pełnych danych kontrahenta**
     Dla **nabywcy i sprzedawcy** wyświetlać pełne dane:

     - nazwa firmy
     - NIP
     - adres
     - numer konta bankowego
     - inne dostępne dane identyfikacyjne

  2. **Łatwe kopiowanie danych**
     - nazwa firmy oraz numer konta powinny być **łatwe do skopiowania**
     - np. kliknięcie w pole kopiuje wartość do schowka

  3. **Cel**
     Ułatwienie wykonywania przelewów oraz szybkiego kopiowania danych kontrahenta do bankowości elektronicznej.

- [IMPROVEMENT] Szybkie kopiowanie kwot w widoku szczegółów faktury
  Obszar: Records / Invoice Details

  Opis:
  W widoku szczegółów faktury dodać możliwość **łatwego kopiowania kluczowych kwot**, analogicznie jak w przypadku danych kontrahenta.

  Pola objęte funkcją kopiowania:

  - kwota netto
  - kwota VAT
  - kwota brutto
  - suma całkowita faktury

  Funkcjonalność:
  - kliknięcie w wartość **kopiuje ją do schowka**
  - opcjonalna ikonka **copy** przy wartości

  Cel:
  Ułatwienie przenoszenia danych do:
  - bankowości elektronicznej
  - arkuszy kalkulacyjnych
  - systemów księgowych.

- [IMPROVEMENT] Podsumowanie pozycji faktury podczas edycji rekordu
  Obszar: Records / Record Form / Invoice Lines

  Opis:
  Podczas wprowadzania lub edycji rekordu zawierającego pozycje faktury dodać sekcję z **automatycznym podsumowaniem pozycji faktury**.

  Funkcjonalność:

  1. **Bieżące sumowanie pozycji**
     System na bieżąco oblicza sumy z wprowadzonych linii faktury:

     - suma netto
     - suma VAT
     - suma brutto

  2. **Widoczna sekcja podsumowania**
     Podsumowanie powinno być widoczne w formularzu (np. pod tabelą pozycji).

  3. **Porównanie z dokumentem źródłowym**
     Użytkownik może łatwo porównać:

     - sumę z wprowadzonych pozycji
     - kwoty z oryginalnej faktury

  Cel:
  Zapobieganie błędom przy ręcznym wprowadzaniu pozycji faktury oraz szybka weryfikacja poprawności danych przed zapisem rekordu.

#Słowniki:

- [FEATURE] Rozszerzenie systemu słowników
  Obszar: Dictionaries / Reference Data

  Opis:
  System posiada obecnie słownik **value types** wykorzystywany przy przypisywaniu typów kosztów.

  Rozważane rozszerzenie systemu słowników o dodatkowe typy danych referencyjnych:

  Możliwe nowe słowniki:

  - **metody płatności**
    - przelew
    - gotówka
    - karta
    - kompensata
    - inne

  - **jednostki miary**
    - szt.
    - m2
    - m3
    - kg
    - godz.

  Charakter funkcjonalności:
  - funkcjonalność **opcjonalna**
  - może zostać dodana w późniejszym etapie rozwoju systemu

  Cel:
  Standaryzacja danych w systemie oraz możliwość łatwego rozszerzania typów danych referencyjnych.

#Użytkownicy:

- [FEATURE] Moduł zarządzania użytkownikami i profilem użytkownika
  Obszar: Users / Authentication

  Opis:
  System posiada obecnie mechanizm tworzenia **głównego użytkownika i organizacji**, a także podstawową obsługę zaproszeń (core istnieje), jednak brakuje widoków oraz panelu użytkownika.

  Do zrealizowania:

  1. **Zapraszanie nowych użytkowników**
     - stworzyć widoki dla istniejącego mechanizmu zaproszeń
     - możliwość zapraszania nowych użytkowników do organizacji

  2. **Panel użytkownika**
     W panelu użytkownika dodać możliwość:

     - zmiany **nazwy wyświetlanej**
     - edycji **metadanych użytkownika**
     - zmiany **hasła logowania**

  3. **Ostatnia aktywność użytkownika**
     - podpiąć aktualizację pola **last_login / last_activity**
     - obecnie pole istnieje, ale nie jest poprawnie aktualizowane

  4. **Sesje użytkownika**
     Aktualnie:
     - sesja ma stały czas życia **12 godzin**

     Zmiana:
     - wprowadzić **sesję zależną od aktywności użytkownika**
     - każda aktywność przedłuża ważność sesji

  Cel:
  Pełna obsługa użytkowników systemu oraz poprawa bezpieczeństwa i ergonomii pracy.

#Role:

- [FEATURE] System ról i uprawnień użytkowników
  Obszar: Users / Authorization

  Opis:
  Wprowadzenie systemu zarządzania uprawnieniami użytkowników w organizacji.

  Wstępna koncepcja ról:

  - **Owner** – właściciel organizacji, pełne uprawnienia
  - **Admin** – zarządzanie danymi i użytkownikami
  - **User** – zwykły użytkownik systemu

  Możliwe rozszerzenie (bardziej elastyczny model):

  - **Owner** zarządza uprawnieniami użytkowników
  - uprawnienia nadawane **per moduł systemu**

  Przykłady modułów:

  - Contracts
  - Counterparties
  - Records
  - Documents
  - Company Finance
  - Users

  Przykładowe uprawnienia:

  - read
  - create
  - edit
  - delete
  - manage

  Wdrożenie:

  - określenie finalnego modelu autoryzacji
  - implementacja kontroli dostępu w modułach systemu

  Priorytet:
  Funkcjonalność wymagana **przed pierwszym releasem systemu**.

  Cel:
  Bezpieczne współdzielenie systemu przez wielu użytkowników oraz kontrola dostępu do danych.

#Subskrybcja:


- [FEATURE] Model subskrypcji i przygotowanie systemu do releasu
  Obszar: SaaS / Deployment / Monetization

  Opis:
  Opracowanie modelu monetyzacji systemu oraz podział funkcjonalności według planów subskrypcyjnych.

  1. **Model subskrypcji**
     Określenie planów abonamentowych systemu (np.):

     - Free / Trial
     - Basic
     - Pro
     - Enterprise

  2. **Podział funkcjonalności**
     System powinien umożliwiać włączanie i wyłączanie funkcji w zależności od planu subskrypcji.

     Przykładowe obszary ograniczeń:

     - liczba użytkowników
     - liczba kontraktów
     - liczba dokumentów
     - funkcje AI
     - funkcje raportowe
     - moduły systemu

  3. **Mechanizm feature gating**
     - implementacja mechanizmu sprawdzania dostępności funkcji dla danego planu

  4. **Przygotowanie środowiska produkcyjnego**
     - przygotowanie **obrazu Docker**
     - konfiguracja deploymentu

  5. **Release systemu**
     - wdrożenie aplikacji na serwer
     - przygotowanie środowiska produkcyjnego

  Cel:
  Umożliwienie komercyjnego wykorzystania systemu jako usługi SaaS oraz przygotowanie do pierwszego releasu.