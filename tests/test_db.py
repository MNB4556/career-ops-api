from __future__ import annotations

from career_ops_api.db import DEFAULT_URL, database_url


def test_default_is_sqlite(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert database_url() == DEFAULT_URL


def test_postgres_scheme_gets_psycopg_driver(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@db:5432/career_ops")
    assert database_url() == "postgresql+psycopg://user:pass@db:5432/career_ops"


def test_postgresql_scheme_gets_psycopg_driver(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@db:5432/career_ops")
    assert database_url() == "postgresql+psycopg://user:pass@db:5432/career_ops"


def test_explicit_driver_is_left_alone(monkeypatch) -> None:
    url = "postgresql+psycopg://user:pass@db:5432/career_ops"
    monkeypatch.setenv("DATABASE_URL", url)
    assert database_url() == url


def test_sqlite_url_is_left_alone(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./local.db")
    assert database_url() == "sqlite:///./local.db"
