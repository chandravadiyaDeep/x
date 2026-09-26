from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.core.db import get_session
from app.models import Assessment, Dataset
from app.services.dataset_service import load_dataframe
from numpa_readiness import assess

router = APIRouter()


class AssessRequest(BaseModel):
    dataset_id: str
    task: str  # "classification" | "regression" | "forecasting" | "clustering"
    target: str | None = None
    stage: str = "initial"  # "initial" | "final"
    weights: dict[str, float] | None = None


def _serialize_result(result) -> dict:
    return {
        "task": result.task,
        "target": result.target,
        "overall_score": result.overall_score,
        "coverage": result.coverage,
        "engine_version": result.engine_version,
        "scoring_config_id": result.scoring_config_id,
        "generated_at": result.generated_at,
        "weights": result.weights,
        "dimensions": [
            {
                "name": d.name,
                "quality": d.quality,
                "weight": d.weight,
                "applicable": d.applicable,
                "checks": [
                    {
                        "id": c.id,
                        "title": c.title,
                        "description": c.description,
                        "status": c.status,
                        "category": c.category,
                        "measurement": c.measurement,
                    }
                    for c in d.checks
                ],
            }
            for d in result.dimensions
        ],
    }


@router.post("/assess")
def run_assessment(payload: AssessRequest):
    with get_session() as session:
        dataset = session.get(Dataset, payload.dataset_id)
        if not dataset:
            raise HTTPException(404, "Dataset not found")

        df = load_dataframe(Path(dataset.storage_path))

        if payload.target and payload.target not in df.columns:
            raise HTTPException(400, f"Target column '{payload.target}' not found in dataset")

        try:
            result = assess(df, task=payload.task, target=payload.target, weights=payload.weights)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc

        record = Assessment(
            dataset_id=dataset.id,
            stage=payload.stage,
            task=result.task,
            target=result.target,
            overall_score=result.overall_score,
            result_json=_serialize_result(result),
        )
        session.add(record)
        session.flush()

        return {"assessment_id": record.id, **_serialize_result(result)}


@router.get("/{dataset_id}")
def list_assessments(dataset_id: str):
    with get_session() as session:
        rows = (
            session.execute(
                select(Assessment).where(Assessment.dataset_id == dataset_id).order_by(Assessment.created_at)
            )
            .scalars()
            .all()
        )
        return [
            {
                "assessment_id": a.id,
                "stage": a.stage,
                "task": a.task,
                "target": a.target,
                "overall_score": a.overall_score,
                "created_at": a.created_at.isoformat(),
            }
            for a in rows
        ]


@router.get("/detail/{assessment_id}")
def get_assessment(assessment_id: str):
    with get_session() as session:
        record = session.get(Assessment, assessment_id)
        if not record:
            raise HTTPException(404, "Assessment not found")
        return {"assessment_id": record.id, "stage": record.stage, **record.result_json}
