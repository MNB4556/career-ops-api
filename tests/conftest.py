from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

# The engine is created at import time, so point it at a throwaway SQLite file
# before any project module is imported. CI sets DATABASE_URL to Postgres and
# that value wins.
if not os.environ.get("DATABASE_URL"):
    tmp_dir = Path(tempfile.mkdtemp(prefix="career-ops-api-"))
    os.environ["DATABASE_URL"] = f"sqlite:///{(tmp_dir / 'test.db').as_posix()}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from career_ops_api import seed as seed_module  # noqa: E402
from career_ops_api.db import Base, engine  # noqa: E402
from career_ops_api.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_schema() -> Iterator[None]:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def seeded() -> None:
    seed_module.seed()
