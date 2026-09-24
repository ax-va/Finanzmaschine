# Database Migrations

## Create a new migration

Example:
```console
$ alembic revision --autogenerate -m "create initial schema"
```

## Apply migrations

Example:
```console
$ alembic upgrade head
```