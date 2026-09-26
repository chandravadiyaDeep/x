from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy import select

from app.core.db import get_session
from app.models import Dataset
from app.services.dataset_service import build_overview, load_dataframe, original_path

router = APIRouter()


@router.post("")
async def upload_dataset(file: UploadFile):
    suffix = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if suffix not in ("csv", "xlsx", "xls"):
        raise HTTPException(400, "Only .csv, .xlsx, and .xls files are supported.")

    with get_session() as session:
        dataset = Dataset(filename=file.filename, storage_path="", n_rows=0, n_cols=0, columns=[], dtypes={})
        session.add(dataset)
        session.flush()  # assigns dataset.id

        dest = original_path(dataset.id, file.filename)
        content = await file.read()
        dest.write_bytes(content)

        try:
            df = load_dataframe(dest)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(400, f"Could not parse file: {exc}") from exc

        overview = build_overview(df)
        dataset.storage_path = str(dest)
        dataset.n_rows = overview["n_rows"]
        dataset.n_cols = overview["n_columns"]
        dataset.columns = overview["columns"]
        dataset.dtypes = overview["dtypes"]

        return {"dataset_id": dataset.id, "filename": dataset.filename, "overview": overview}


@router.get("")
def list_datasets():
    with get_session() as session:
        rows = session.execute(select(Dataset).order_by(Dataset.uploaded_at.desc())).scalars().all()
        return [
            {
                "dataset_id": d.id,
                "filename": d.filename,
                "n_rows": d.n_rows,
                "n_cols": d.n_cols,
                "uploaded_at": d.uploaded_at.isoformat(),
            }
            for d in rows
        ]


@router.get("/{dataset_id}")
def get_dataset(dataset_id: str):
    with get_session() as session:
        dataset = session.get(Dataset, dataset_id)
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        df = load_dataframe(Path(dataset.storage_path))
        return {
            "dataset_id": dataset.id,
            "filename": dataset.filename,
            "uploaded_at": dataset.uploaded_at.isoformat(),
            "overview": build_overview(df),
        }
