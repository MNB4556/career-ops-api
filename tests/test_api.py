from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient

from career_ops_api.seed import POSTINGS, seed


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_serves_the_demo_page(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "career-ops API" in response.text
    assert "/docs" in response.text


def test_empty_database_returns_empty_list(client: TestClient) -> None:
    response = client.get("/postings")
    assert response.status_code == 200
    assert response.json() == []


def test_seed_is_idempotent(seeded: None, client: TestClient) -> None:
    first = client.get("/stats").json()
    seed(reset=False)
    second = client.get("/stats").json()
    assert first == second
    assert first["postings"] == len(POSTINGS)


def test_list_postings_is_newest_first(seeded: None, client: TestClient) -> None:
    rows = client.get("/postings", params={"limit": 100}).json()
    assert len(rows) == len(POSTINGS)
    dates = [row["posted_at"] for row in rows]
    assert dates == sorted(dates, reverse=True)
    assert set(rows[0]) == {
        "id",
        "source",
        "title",
        "company",
        "location",
        "url",
        "salary_min",
        "salary_max",
        "posted_at",
    }


def test_pagination_does_not_overlap(seeded: None, client: TestClient) -> None:
    first = client.get("/postings", params={"limit": 5}).json()
    second = client.get("/postings", params={"limit": 5, "offset": 5}).json()
    assert len(first) == 5
    assert len(second) == 5
    assert {row["id"] for row in first}.isdisjoint({row["id"] for row in second})


def test_search_matches_title_and_company(seeded: None, client: TestClient) -> None:
    by_title = client.get("/postings", params={"q": "backend"}).json()
    assert by_title
    assert all("backend" in (row["title"] + row["company"]).lower() for row in by_title)

    by_company = client.get("/postings", params={"q": "northwind"}).json()
    assert [row["company"] for row in by_company] == ["Northwind Systems"]


def test_source_filter(seeded: None, client: TestClient) -> None:
    rows = client.get("/postings", params={"source": "Adzuna", "limit": 100}).json()
    assert rows
    assert all(row["source"] == "Adzuna" for row in rows)


def test_unknown_source_returns_empty_list(seeded: None, client: TestClient) -> None:
    response = client.get("/postings", params={"source": "Nowhere"})
    assert response.status_code == 200
    assert response.json() == []


def test_limit_out_of_range_is_rejected(client: TestClient) -> None:
    assert client.get("/postings", params={"limit": 101}).status_code == 422
    assert client.get("/postings", params={"limit": 0}).status_code == 422
    assert client.get("/postings", params={"offset": -1}).status_code == 422


def test_get_posting_returns_description(seeded: None, client: TestClient) -> None:
    listed = client.get("/postings", params={"limit": 1}).json()[0]
    response = client.get(f"/postings/{listed['id']}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == listed["id"]
    assert body["description"]


def test_get_missing_posting_returns_404(client: TestClient) -> None:
    response = client.get("/postings/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "posting not found"


def test_create_application_defaults_to_today(seeded: None, client: TestClient) -> None:
    posting_id = client.get("/postings", params={"limit": 1}).json()[0]["id"]
    response = client.post(
        "/applications",
        json={"posting_id": posting_id, "status": "applied", "notes": "Sent CV."},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["posting_id"] == posting_id
    assert body["applied_on"] == date.today().isoformat()
    assert body["notes"] == "Sent CV."


def test_create_application_accepts_explicit_date(seeded: None, client: TestClient) -> None:
    posting_id = client.get("/postings", params={"limit": 1}).json()[0]["id"]
    response = client.post(
        "/applications",
        json={
            "posting_id": posting_id,
            "status": "interview",
            "applied_on": "2026-10-01",
            "notes": "",
        },
    )
    assert response.status_code == 201
    assert response.json()["applied_on"] == "2026-10-01"


def test_create_application_for_missing_posting_returns_404(
    client: TestClient,
) -> None:
    response = client.post("/applications", json={"posting_id": 999999})
    assert response.status_code == 404


def test_create_application_rejects_bad_status(seeded: None, client: TestClient) -> None:
    posting_id = client.get("/postings", params={"limit": 1}).json()[0]["id"]
    response = client.post(
        "/applications",
        json={"posting_id": posting_id, "status": "ghosted"},
    )
    assert response.status_code == 422


def test_create_application_rejects_long_notes(seeded: None, client: TestClient) -> None:
    posting_id = client.get("/postings", params={"limit": 1}).json()[0]["id"]
    response = client.post(
        "/applications",
        json={"posting_id": posting_id, "notes": "x" * 2001},
    )
    assert response.status_code == 422


def test_stats_counts_sources_and_statuses(seeded: None, client: TestClient) -> None:
    body = client.get("/stats").json()
    assert body["postings"] == len(POSTINGS)
    assert sum(body["sources"].values()) == len(POSTINGS)
    assert body["applications"] == {
        "applied": 1,
        "interview": 1,
        "screening": 1,
        "rejected": 1,
    }


def test_stats_reflect_new_applications(seeded: None, client: TestClient) -> None:
    posting_id = client.get("/postings", params={"limit": 1}).json()[0]["id"]
    client.post("/applications", json={"posting_id": posting_id, "status": "offer"})
    body = client.get("/stats").json()
    assert body["applications"]["offer"] == 1
