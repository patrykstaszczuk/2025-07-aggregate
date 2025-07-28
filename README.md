# 2025-07-aggregate

## Local

Przed wprowadzeniem jakichkolwiek zmian, uruchom poniższe polecenie, aby przygotować środowisko. <br>
Polecenie stworzy wirtualne środowisko, zainstaluje potrzebne bibloteki oraz pre-commit'a

```bash
make init
```

## Uruchomienie projektu w trybie developerskim

Do uruchomienia projektu potrzebujesz **Dockera**. oraz pliku .env ze zmiennymi zdefiniowanymi w .env.example

Uruchom projekt poleceniem:

```bash
docker-compose -f docker-compose-dev.yml up
```

## Testy
Projekt posiada testy integracyjne oraz jednostkowe. Do uruchomienia testów potrzebujesz pytest. Testy uruchamiasz poleceniem:
`python -m pytest`

Testy uruchamiane są take przy każdym commicie

Podział testów:
- integracyjne - łączące kilka modułów i/lub korzystające z bazy danych
- jednostkowe - szybkie testy do konkretnych funkcjonalności

## Migracje bazy danych
Do migracji używany jest alembic

Aby uruchomić migracje należy wykonać polecenie:
``alembic revision --autogenerate -m "krótki opis zmia" `` (połączenie z bazą danych musi być możliwe)

migracja aplikowana jest w momencie startu aplikacji w docker-compose


## Decyzje architektoinczne
- przetwarzanie pliku asynchronicznie ze względu na możliwe rozmiary .csv czyli setki tysięcy wierszy
- użycie testcontainers w testach. Pozwala na testowanie z użyciem prawdziwej bazy danych w łatwy sposób
- podział na jak najmniejsze komponenty, jasny rozdział obowiązków
- importy relatywne vs absolutne. Importy relatywne używe w obrębie jednego modułu w celu jasnego zadeklarowana
co jest importowane z danego modułu a co nie.
Importy absulutne służą do importowania zależności z poza modułu



## Dalsze propozycje rozwoju projektu oraz optymalizacji
- implementacja filtrowania raportów po datach
- przeniesienie mechanizmu filtrowania do oddzielnej klasy (analogicznie do paginacji)
- stworzenie produkcyjnego docker-compose.yml
- stworzenie mechanizmu śledzenia importów poprzez zapis żądania importu w bazie danych oraz jego odczyt poprzez API np.
w celu uzyskania statusu żądania, liczby przetworzonych wierszy, liczby błędów, czy pliku z błędnymi wierszami
- błędne wiersze oprócz logowania powinny być zapisywane w pliku z błędami i udostępniane przez API w celu pobrania. Z użyciem mechanizmu śledzenia żądań importów
- użycie Decimal zamiast float do operacji na kwotach
- usuwanie plików po ich przetworzeniu
- implementacja github actions do automatycznych testów e2e i CICD
- implementacja lepszej autoryzacji

Przykładowa struktura modelu do Importów

```
class Import:
 id: uuid  -> przekazane w zwrotce w POST /transactions/upload
 status: ImportStatus
 orginal_file_name: str
 errors_report_file_path: str  # S3 lub local
 created_at: datetime
 finished_at: datetime
 processed_rows: int
 rows_with_errors: int

```
