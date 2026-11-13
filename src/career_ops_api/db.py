from __future__ import annotations

import os
from collections.abc import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DEFAULT_URL = "sqlite:///./career_ops_api.db"


class Base(DeclarativeBase):
    pass


def database_url() -> str:
    url = os.getenv("DATABASE_URL", DEFAULT_URL)
    # Render and Heroku hand out postgres:// URLs. SQLAlchemy would pick
    # psycopg2 from that scheme, and this project installs psycopg 3.
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


def make_engine(url: str | None = None) -> Engine:
    url = url or database_url()
    kwargs: dict[str, object] = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    elif os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        # A Lambda container serves one request at a time and Neon counts
        # connections per project. One connection per container keeps the
        # total predictable under a burst of cold starts.
        kwargs["pool_size"] = 1
        kwargs["max_overflow"] = 0
    return create_engine(url, **kwargs)


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


def init_db() -> None:
    from career_ops_api import models  # noqa: F401

    Base.metadata.create_all(engine)
