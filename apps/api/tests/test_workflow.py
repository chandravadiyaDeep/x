import io

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("NUMPA_STORAGE_DIR", str(tmp_path / "datasets"))
    monkeypatch.setenv("NUMPA_DATABASE_URL", f"sqlite:///{tmp_path / 'numpa.db'}")
    # settings is a module-level singleton already constructed on import elsewhere,
    # so tests run in a fresh process per test session via pytest-xdist boundaries;
    # for a single-process run we accept the default paths and just isolate the DB file.
    with TestClient(app) as c:
        yield c


def _sample_csv_bytes() -> bytes:
    rng = np.random.default_rng(42)
    n = 200
    df = pd.DataFrame(
        {
            "tenure_months": rng.integers(1, 72, n).astype(float),
            "monthly_charges": rng.normal(65, 20, n),
            "contract_type": rng.choice(["monthly", "one_year", "two_year"], n),
            "churned": rng.choice([0, 1], n, p=[0.85, 0.15]),
        }
    )
    df.loc[rng.choice(n, 10, replace=False), "monthly_charges"] = np.nan
    return df.to_csv(index=False).encode()


def test_full_workflow(client):
    r = client.post("/v1/datasets", files={"file": ("churn.csv", io.BytesIO(_sample_csv_bytes()), "text/csv")})
    assert r.status_code == 200
    dataset_id = r.json()["dataset_id"]
    assert r.json()["overview"]["n_rows"] == 200

    r2 = client.post(
        "/v1/readiness/assess",
        json={"dataset_id": dataset_id, "task": "classification", "target": "churned", "stage": "initial"},
    )
    assert r2.status_code == 200
    assert r2.json()["overall_score"] is not None

    r3 = client.post(
        "/v1/cleaning/run",
        json={
            "dataset_id": dataset_id,
            "steps": [
                {"id": "s1", "type": "impute_missing_values", "params": {"strategy": "median"}},
                {"id": "s2", "type": "remove_duplicates", "params": {}},
            ],
        },
    )
    assert r3.status_code == 200

    r4 = client.get(f"/v1/reports/overview/{dataset_id}")
    assert r4.status_code == 200
    assert r4.headers["content-type"] == "application/pdf"


def test_missing_dataset_404(client):
    r = client.post(
        "/v1/readiness/assess",
        json={"dataset_id": "does-not-exist", "task": "classification", "target": "x"},
    )
    assert r.status_code == 404


def test_unsupported_file_type_rejected(client):
    r = client.post("/v1/datasets", files={"file": ("data.json", io.BytesIO(b"{}"), "application/json")})
    assert r.status_code == 400
