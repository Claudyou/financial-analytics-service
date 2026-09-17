import io

import pytest
from fastapi.testclient import TestClient

from app.api.router import get_import_service
from app.main import app
from app.repositories.transaction_repository import TransactionRepository
from app.services.import_service import ImportService

VALID_CSV = (
    "transaction_date,amount,currency,description,account_id\n"
    "2026-09-01,-45.50,RON,LIDL,account_1\n"
    "2026-09-02,5000.00,RON,Salary,account_1\n"
)


@pytest.fixture
def client() -> TestClient:
    """A client whose import service uses a fresh in-memory repository."""
    repository = TransactionRepository()
    app.dependency_overrides[get_import_service] = lambda: ImportService(repository)
    yield TestClient(app)
    app.dependency_overrides.clear()


def _upload(content: str) -> dict:
    return {"file": ("transactions.csv", io.BytesIO(content.encode()), "text/csv")}


def test_valid_csv_creates_transactions(client: TestClient) -> None:
    response = client.post("/imports", files=_upload(VALID_CSV))

    assert response.status_code == 201
    assert response.json() == {
        "created": 2,
        "duplicates_skipped": 0,
        "invalid_rows": 0,
    }


def test_missing_required_column_returns_422(client: TestClient) -> None:
    csv_without_amount = (
        "transaction_date,currency,description,account_id\n"
        "2026-09-01,RON,LIDL,account_1\n"
    )

    response = client.post("/imports", files=_upload(csv_without_amount))

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "invalid_csv_columns"
    assert body["details"]["missing_columns"] == ["amount"]


def test_repeated_import_skips_duplicates(client: TestClient) -> None:
    first = client.post("/imports", files=_upload(VALID_CSV))
    assert first.json()["created"] == 2

    second = client.post("/imports", files=_upload(VALID_CSV))

    assert second.status_code == 201
    assert second.json() == {
        "created": 0,
        "duplicates_skipped": 2,
        "invalid_rows": 0,
    }


def test_invalid_rows_are_counted_and_skipped(client: TestClient) -> None:
    csv_with_bad_rows = (
        "transaction_date,amount,currency,description,account_id\n"
        "2026-09-01,-45.50,RON,LIDL,account_1\n"
        "not-a-date,10.00,RON,Coffee,account_1\n"
        "2026-09-03,0,RON,Zero,account_1\n"
    )

    response = client.post("/imports", files=_upload(csv_with_bad_rows))

    assert response.status_code == 201
    assert response.json() == {
        "created": 1,
        "duplicates_skipped": 0,
        "invalid_rows": 2,
    }


def test_missing_file_returns_400(client: TestClient) -> None:
    response = client.post("/imports")

    assert response.status_code == 400
    assert response.json()["code"] == "file_missing"
