from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from career_ops_api.db import get_session, init_db
from career_ops_api.models import Application, Posting
from career_ops_api.schemas import (
    ApplicationIn,
    ApplicationOut,
    PostingDetail,
    PostingOut,
    StatsOut,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="career-ops demo API",
    version="0.1.1",
    description="Endpoints over synthetic job-search data.",
    lifespan=lifespan,
)

SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/postings", response_model=list[PostingOut])
def list_postings(
    session: SessionDep,
    q: str | None = Query(default=None, max_length=100),
    source: str | None = Query(default=None, max_length=40),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[Posting]:
    stmt = select(Posting).order_by(Posting.posted_at.desc(), Posting.id.desc())
    if q:
        pattern = f"%{q.lower()}%"
        stmt = stmt.where(
            func.lower(Posting.title).like(pattern) | func.lower(Posting.company).like(pattern)
        )
    if source:
        stmt = stmt.where(Posting.source == source)
    stmt = stmt.limit(limit).offset(offset)
    return list(session.scalars(stmt))


@app.get("/postings/{posting_id}", response_model=PostingDetail)
def get_posting(posting_id: int, session: SessionDep) -> Posting:
    posting = session.get(Posting, posting_id)
    if posting is None:
        raise HTTPException(status_code=404, detail="posting not found")
    return posting


@app.post("/applications", response_model=ApplicationOut, status_code=201)
def create_application(body: ApplicationIn, session: SessionDep) -> Application:
    if session.get(Posting, body.posting_id) is None:
        raise HTTPException(status_code=404, detail="posting not found")

    application = Application(
        posting_id=body.posting_id,
        status=body.status,
        applied_on=body.applied_on or date.today(),
        notes=body.notes,
    )
    session.add(application)
    session.commit()
    session.refresh(application)
    return application


@app.get("/stats", response_model=StatsOut)
def stats(session: SessionDep) -> StatsOut:
    total = session.scalar(select(func.count()).select_from(Posting)) or 0
    sources = dict(
        session.execute(select(Posting.source, func.count()).group_by(Posting.source)).all()
    )
    applications = dict(
        session.execute(select(Application.status, func.count()).group_by(Application.status)).all()
    )
    return StatsOut(postings=total, sources=sources, applications=applications)
