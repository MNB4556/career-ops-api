from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from career_ops_api.db import Base


class Posting(Base):
    __tablename__ = "postings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(40), index=True)
    external_id: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(200), index=True)
    company: Mapped[str] = mapped_column(String(120))
    location: Mapped[str] = mapped_column(String(120))
    url: Mapped[str] = mapped_column(String(500))
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    posted_at: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(Text, default="")

    applications: Mapped[list[Application]] = relationship(back_populates="posting")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    posting_id: Mapped[int] = mapped_column(ForeignKey("postings.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), index=True)
    applied_on: Mapped[date] = mapped_column(Date)
    notes: Mapped[str] = mapped_column(Text, default="")

    posting: Mapped[Posting] = relationship(back_populates="applications")
