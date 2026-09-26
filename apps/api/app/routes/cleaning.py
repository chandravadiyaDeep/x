from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.core.db import get_session
from app.models import Dataset, PipelineExecution
from app.services.dataset_service import cleaned_path, load_dataframe
from numpa_cleaning import PipelineStep, run_pipeline
from numpa_cleaning.operations import OPERATIONS

router = APIRouter()


class StepPayload(BaseModel):
    id: str
    type: str
    params: dict = {}


class RunPipelineRequest(BaseModel):
    dataset_id: str
    name: str | None = None
    steps: list[StepPayload]


@router.get("/operations")
def list_operations():
    """Single source of truth for what operations exist, so the frontend
    never maintains a second, conflicting list."""
    return {"operations": list(OPERATIONS.keys())}


@router.post("/run")
def run_cleaning_pipeline(payload: RunPipelineRequest):
    with get_session() as session:
        dataset = session.get(Dataset, payload.dataset_id)
        if not dataset:
            raise HTTPException(404, "Dataset not found")

        df = load_dataframe(Path(dataset.storage_path))
        steps = [PipelineStep(id=s.id, type=s.type, params=s.params) for s in payload.steps]

        try:
            result = run_pipeline(df, steps)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc

        record = PipelineExecution(
            dataset_id=dataset.id,
            name=payload.name,
            steps_json=[s.__dict__ for s in steps],
            result_json=result.to_dict(),
            cleaned_storage_path="",
        )
        session.add(record)
        session.flush()

        out_path = cleaned_path(dataset.id, record.id)
        result.cleaned_df.to_csv(out_path, index=False)
        record.cleaned_storage_path = str(out_path)

        return {
            "execution_id": record.id,
            **result.to_dict(),
            "cleaned_preview": result.cleaned_df.head(10).where(
                result.cleaned_df.notna(), None
            ).to_dict(orient="records"),
        }


@router.get("/{dataset_id}")
def list_executions(dataset_id: str):
    with get_session() as session:
        rows = (
            session.execute(
                select(PipelineExecution)
                .where(PipelineExecution.dataset_id == dataset_id)
                .order_by(PipelineExecution.created_at)
            )
            .scalars()
            .all()
        )
        return [
            {
                "execution_id": e.id,
                "name": e.name,
                "created_at": e.created_at.isoformat(),
                "original_rows": e.result_json.get("original_rows"),
                "final_rows": e.result_json.get("final_rows"),
                "step_count": len(e.result_json.get("steps", [])),
            }
            for e in rows
        ]
