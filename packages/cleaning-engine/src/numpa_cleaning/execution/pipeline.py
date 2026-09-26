from __future__ import annotations

import datetime as dt
from dataclasses import asdict, dataclass, field

import pandas as pd

from ..operations import OPERATIONS


@dataclass
class PipelineStep:
    """One configured step in a cleaning pipeline (the *definition*, not a run of it)."""

    id: str
    type: str  # must be a key in OPERATIONS
    params: dict = field(default_factory=dict)


@dataclass
class StepExecutionRecord:
    step_id: str
    type: str
    params: dict
    summary: str
    measurements: dict
    warnings: list[str]
    rows_before: int
    rows_after: int
    columns_before: list[str]
    columns_after: list[str]


@dataclass
class PipelineExecutionResult:
    cleaned_df: pd.DataFrame
    steps: list[StepExecutionRecord]
    executed_at: str
    original_rows: int
    final_rows: int

    def to_dict(self) -> dict:
        return {
            "executed_at": self.executed_at,
            "original_rows": self.original_rows,
            "final_rows": self.final_rows,
            "steps": [asdict(s) for s in self.steps],
        }


def run_pipeline(df: pd.DataFrame, steps: list[PipelineStep]) -> PipelineExecutionResult:
    """
    Executes steps in order against a copy of the original dataframe.
    The caller is responsible for keeping the original dataset (this
    function never mutates the input).
    """
    working_df = df.copy()
    records: list[StepExecutionRecord] = []

    for step in steps:
        if step.type not in OPERATIONS:
            raise ValueError(f"Unknown operation type: {step.type}")

        op_fn = OPERATIONS[step.type]
        rows_before, cols_before = len(working_df), list(working_df.columns)

        new_df, meta = op_fn(working_df, step.params)

        records.append(
            StepExecutionRecord(
                step_id=step.id,
                type=step.type,
                params=step.params,
                summary=meta.get("summary", ""),
                measurements=meta.get("measurements", {}),
                warnings=meta.get("warnings", []),
                rows_before=rows_before,
                rows_after=len(new_df),
                columns_before=cols_before,
                columns_after=list(new_df.columns),
            )
        )
        working_df = new_df

    return PipelineExecutionResult(
        cleaned_df=working_df,
        steps=records,
        executed_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        original_rows=len(df),
        final_rows=len(working_df),
    )
