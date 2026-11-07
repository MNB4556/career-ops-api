# career-ops API

A small API over synthetic job-search data. It exists to show the
parts of backend work that a local CLI does not: an HTTP API, Pydantic request
and response models, a server database, containers, and a pipeline that tests,
builds and publishes an image.

The data is fictional. There is no connection to the real
[career-ops](https://github.com/MNB4556/career-ops) database, and the CLI is not
modified by this repo.

## Endpoints

| Method | Path | What it does |
| --- | --- | --- |
| GET | `/health` | Liveness check used by the container healthcheck |
| GET | `/postings` | List postings, newest first. Filters: `q`, `source`, `limit`, `offset` |
| GET | `/postings/{id}` | One posting with its description |
| POST | `/applications` | Record an application against a posting |
| GET | `/stats` | Counts by source and by application status |

Interactive docs are served at `/docs` and the schema at `/openapi.json`.

`POST /applications` is the only write. Everything else is read-only. There is no
authentication, so the deployment either stays private or accepts that anyone can
add a row to the demo table.

## Run locally

Python 3.11 or newer.

```sh
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS and Linux
pip install -e ".[dev]"
python -m career_ops_api.seed
uvicorn career_ops_api.main:app --reload
```

The default database is SQLite at `./career_ops_api.db`. Point `DATABASE_URL` at
Postgres to use the server database instead:

```sh
set DATABASE_URL=postgresql+psycopg://career:career@localhost:5432/career_ops
```

The schema is created on startup. The seed script replaces the rows unless you
pass `--keep`, which seeds only an empty database.

## Tests

```sh
pytest -q
```

The suite runs against SQLite by default and against Postgres when `DATABASE_URL`
points there. `tests/test_postgres.py` skips itself on SQLite, so the CI Postgres
job is the thing that proves the schema and queries are not SQLite-specific.

## Containers

```sh
docker compose up --build
```

This starts Postgres and the API. Compose seeds the database on first start and
then leaves it alone. The API is on `http://localhost:8000`, docs on
`http://localhost:8000/docs`.

The image is a single stage on `python:3.12-slim`, installs the package, and runs
as a non-root user. It exposes a `HEALTHCHECK` that calls `/health`.

## CI and deployment

`.github/workflows/ci.yml` does four things:

1. Runs ruff and pytest on Python 3.11 and 3.12.
2. Runs the same suite against a Postgres 16 service container.
3. Builds the image on every push and pull request.
4. On `main`, pushes the image to GHCR and calls `DEPLOY_WEBHOOK_URL` if that
   secret is set.

There is no live URL yet. The deploy step is wired but idle until a host is
chosen and the secret exists. The host needs to run the image with
`DATABASE_URL` set and seed the database once with
`python -m career_ops_api.seed --keep`.

## Stack

FastAPI, SQLAlchemy 2, Pydantic 2, psycopg 3, uvicorn, pytest and ruff.
