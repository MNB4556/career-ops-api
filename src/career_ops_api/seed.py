"""Fill the database with fictional postings and applications.

Every company, salary and URL here is invented. The seed never reads the real
career-ops database and never writes to it.
"""

from __future__ import annotations

import argparse
from datetime import date

from sqlalchemy import delete, func, select

from career_ops_api.db import SessionLocal, init_db
from career_ops_api.models import Application, Posting

POSTINGS = [
    {
        "source": "Adzuna",
        "external_id": "demo-1001",
        "title": "Junior Python Developer",
        "company": "Northwind Systems",
        "location": "Bristol",
        "url": "https://example.com/jobs/1001",
        "salary_min": 28000,
        "salary_max": 34000,
        "posted_at": date(2026, 11, 2),
        "description": "Small team building internal tools in Python and PostgreSQL.",
    },
    {
        "source": "Adzuna",
        "external_id": "demo-1002",
        "title": "Backend Engineer (Graduate)",
        "company": "Harbour Labs",
        "location": "London",
        "url": "https://example.com/jobs/1002",
        "salary_min": 32000,
        "salary_max": 38000,
        "posted_at": date(2026, 10, 30),
        "description": "REST services for a logistics product. Some on-call after training.",
    },
    {
        "source": "Remotive",
        "external_id": "demo-1003",
        "title": "Python Developer",
        "company": "Fernway Digital",
        "location": "Remote (UK)",
        "url": "https://example.com/jobs/1003",
        "salary_min": 35000,
        "salary_max": 45000,
        "posted_at": date(2026, 10, 29),
        "description": "Maintain a set of data-ingestion services. Fully remote in the UK.",
    },
    {
        "source": "Arbeitnow",
        "external_id": "demo-1004",
        "title": "Software Engineer",
        "company": "Kestrel Data",
        "location": "Manchester",
        "url": "https://example.com/jobs/1004",
        "salary_min": 30000,
        "salary_max": 36000,
        "posted_at": date(2026, 10, 27),
        "description": "Hybrid role working on a reporting platform used by retailers.",
    },
    {
        "source": "Remote OK",
        "external_id": "demo-1005",
        "title": "Junior Platform Engineer",
        "company": "Mersey Cloud",
        "location": "Liverpool",
        "url": "https://example.com/jobs/1005",
        "salary_min": 30000,
        "salary_max": 40000,
        "posted_at": date(2026, 10, 25),
        "description": "Containers, deployments and developer tooling for a small platform team.",
    },
    {
        "source": "Adzuna",
        "external_id": "demo-1006",
        "title": "Graduate Developer",
        "company": "Alder & Co",
        "location": "Leeds",
        "url": "https://example.com/jobs/1006",
        "salary_min": 27000,
        "salary_max": 31000,
        "posted_at": date(2026, 10, 24),
        "description": "Two-year graduate scheme rotating through web and data teams.",
    },
    {
        "source": "Arbeitnow",
        "external_id": "demo-1007",
        "title": "Backend Developer (Python)",
        "company": "Beacon Health",
        "location": "Birmingham",
        "url": "https://example.com/jobs/1007",
        "salary_min": 33000,
        "salary_max": 39000,
        "posted_at": date(2026, 10, 22),
        "description": "APIs for appointment scheduling. Healthcare background is not required.",
    },
    {
        "source": "Remotive",
        "external_id": "demo-1008",
        "title": "Full-Stack Developer",
        "company": "Orchard Studio",
        "location": "London",
        "url": "https://example.com/jobs/1008",
        "salary_min": 34000,
        "salary_max": 42000,
        "posted_at": date(2026, 10, 20),
        "description": "React front end and a Python API. Agency setting, several clients.",
    },
    {
        "source": "Adzuna",
        "external_id": "demo-1009",
        "title": "Data Engineer",
        "company": "Lumen Analytics",
        "location": "Edinburgh",
        "url": "https://example.com/jobs/1009",
        "salary_min": 32000,
        "salary_max": 40000,
        "posted_at": date(2026, 10, 18),
        "description": "Batch pipelines and warehouse maintenance. SQL-heavy role.",
    },
    {
        "source": "Hacker News",
        "external_id": "demo-1010",
        "title": "Software Engineer (Tools)",
        "company": "Pillar Games",
        "location": "Remote (UK)",
        "url": "https://example.com/jobs/1010",
        "salary_min": 30000,
        "salary_max": 45000,
        "posted_at": date(2026, 10, 16),
        "description": "Internal tools for an art and engineering team. Posted in a hiring thread.",
    },
    {
        "source": "Remote OK",
        "external_id": "demo-1011",
        "title": "Junior DevOps Engineer",
        "company": "Cobalt Systems",
        "location": "Glasgow",
        "url": "https://example.com/jobs/1011",
        "salary_min": 28000,
        "salary_max": 35000,
        "posted_at": date(2026, 10, 14),
        "description": "CI pipelines and infrastructure support. Training provided.",
    },
    {
        "source": "Adzuna",
        "external_id": "demo-1012",
        "title": "API Developer",
        "company": "Sable Finance",
        "location": "London",
        "url": "https://example.com/jobs/1012",
        "salary_min": 36000,
        "salary_max": 44000,
        "posted_at": date(2026, 10, 12),
        "description": "Design and maintain public HTTP APIs for a payments product.",
    },
]

APPLICATIONS = [
    {
        "external_id": "demo-1001",
        "status": "applied",
        "applied_on": date(2026, 11, 2),
        "notes": "Sent CV.",
    },
    {
        "external_id": "demo-1003",
        "status": "interview",
        "applied_on": date(2026, 10, 30),
        "notes": "First call booked.",
    },
    {
        "external_id": "demo-1007",
        "status": "screening",
        "applied_on": date(2026, 10, 25),
        "notes": "Recruiter asked for salary.",
    },
    {
        "external_id": "demo-1009",
        "status": "rejected",
        "applied_on": date(2026, 10, 19),
        "notes": "Role filled internally.",
    },
]


def seed(reset: bool = True) -> None:
    init_db()
    with SessionLocal() as session:
        existing = session.scalar(select(func.count()).select_from(Posting)) or 0
        if existing and not reset:
            print(f"{existing} postings already present, nothing to do")
            return
        if reset:
            session.execute(delete(Application))
            session.execute(delete(Posting))
            session.commit()

        session.add_all([Posting(**row) for row in POSTINGS])
        session.flush()
        ids_by_external = {
            posting.external_id: posting.id for posting in session.scalars(select(Posting)).all()
        }
        session.add_all(
            [
                Application(
                    posting_id=ids_by_external[row["external_id"]],
                    status=row["status"],
                    applied_on=row["applied_on"],
                    notes=row["notes"],
                )
                for row in APPLICATIONS
            ]
        )
        session.commit()
        print(f"seeded {len(POSTINGS)} postings and {len(APPLICATIONS)} applications")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the demo database.")
    parser.add_argument(
        "--keep",
        action="store_true",
        help="leave existing rows alone instead of replacing them",
    )
    args = parser.parse_args()
    seed(reset=not args.keep)


if __name__ == "__main__":
    main()
