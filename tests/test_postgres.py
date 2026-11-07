"""Checks that only run when the suite is pointed at Postgres.

The rest of the suite exercises the same code paths against SQLite. This file
exists so the CI Postgres job proves the schema and queries work on a server
database too, not just on SQLite.
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy import text

from career_ops_api.db import engine

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL", "").startswith("postgresql"),
    reason="set DATABASE_URL to a Postgres URL to run these",
)


def test_engine_is_postgres() -> None:
    assert engine.dialect.name == "postgresql"


def test_round_trip_on_postgres(client) -> None:
    from career_ops_api.seed import POSTINGS, seed

    seed()
    rows = client.get("/postings", params={"limit": 100}).json()
    assert len(rows) == len(POSTINGS)
    assert client.get("/stats").json()["postings"] == len(POSTINGS)


def test_select_one() -> None:
    with engine.connect() as connection:
        assert connection.execute(text("select 1")).scalar_one() == 1
