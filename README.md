# 2025-07-aggregate

## Local

Przed wprowadzeniem jakichkolwiek zmian, uruchom poniższe polecenie, aby przygotować środowisko:

```bash
make init
```

## Uruchomienie projektu w trybie developerskim

Do uruchomienia projektu potrzebujesz **Dockera**.

Uruchom projekt poleceniem:

```bash
docker-compose -f docker-compose-dev.yml up
```

## Migracje bazy danych
Do migracji używany jest alembic

Aby uruchomić migracje należy wykonać polecenie:
``alembic revision --autogenerate -m "krótki opis zmia" `` (połączenie z bazą danych musi być możliwe)

migracja aplikowana jest w momencie startu aplikacji w docker-compose
