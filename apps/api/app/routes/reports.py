from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.db import get_session
from app.models import Assessment, Dataset
from app.services.dataset_service import build_overview, load_dataframe
from app.services.report_service import generate_assessment_report, generate_overview_report

router = APIRouter()


@router.get("/overview/{dataset_id}")
def overview_report(dataset_id: str):
    with get_session() as session:
        dataset = session.get(Dataset, dataset_id)
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        df = load_dataframe(Path(dataset.storage_path))
        overview = build_overview(df)
        out_path = Path(dataset.storage_path).parent / "overview_report.pdf"
        generate_overview_report(dataset.filename, overview, out_path)
        return FileResponse(out_path, filename=f"{dataset.filename}_overview.pdf", media_type="application/pdf")


@router.get("/assessment/{assessment_id}")
def assessment_report(assessment_id: str):
    with get_session() as session:
        record = session.get(Assessment, assessment_id)
        if not record:
            raise HTTPException(404, "Assessment not found")
        dataset = session.get(Dataset, record.dataset_id)
        out_path = Path(dataset.storage_path).parent / f"assessment_{record.id}.pdf"
        generate_assessment_report(dataset.filename, {"stage": record.stage, **record.result_json}, out_path)
        return FileResponse(
            out_path, filename=f"{dataset.filename}_{record.stage}_readiness.pdf", media_type="application/pdf"
        )
