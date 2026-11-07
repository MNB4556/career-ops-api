from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Status = Literal["applied", "screening", "interview", "offer", "rejected", "withdrawn"]


class PostingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    title: str
    company: str
    location: str
    url: str
    salary_min: int | None
    salary_max: int | None
    posted_at: date


class PostingDetail(PostingOut):
    description: str


class ApplicationIn(BaseModel):
    posting_id: int = Field(gt=0)
    status: Status = "applied"
    applied_on: date | None = None
    notes: str = Field(default="", max_length=2000)


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    posting_id: int
    status: Status
    applied_on: date
    notes: str


class StatsOut(BaseModel):
    postings: int
    sources: dict[str, int]
    applications: dict[str, int]
