"""
The scoring engine: runs applicable checks and combines them into a single,
explainable readiness assessment result.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import asdict, dataclass, field

import pandas as pd

from .config import DEFAULT_CONFIG_ID, DEFAULT_WEIGHTS, ENGINE_VERSION, SUPPORTED_TASKS
from ..checks import DimensionResult
from ..checks.structure import check_completeness, check_record_integrity, check_validity_consistency
from ..checks.task import check_data_sufficiency, check_feature_suitability, check_target_suitability
from ..leakage.detectors import check_leakage_validation


@dataclass
class AssessmentResult:
    task: str
    target: str | None
    overall_score: float | None
    dimensions: list[DimensionResult]
    coverage: dict
    engine_version: str
    scoring_config_id: str
    generated_at: str
    weights: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


def assess(
    df: pd.DataFrame,
    task: str,
    target: str | None = None,
    weights: dict[str, float] | None = None,
) -> AssessmentResult:
    if task not in SUPPORTED_TASKS:
        raise ValueError(f"Unsupported task '{task}'. Supported: {SUPPORTED_TASKS}")

    weights = weights or DEFAULT_WEIGHTS

    dims: list[DimensionResult] = [
        check_completeness(df, weights["completeness"]),
        check_validity_consistency(df, weights["validity_consistency"]),
        check_record_integrity(df, weights["record_integrity"]),
        check_feature_suitability(df, target, weights["feature_suitability"]),
        check_target_suitability(df, target, task, weights["target_suitability"]),
        check_data_sufficiency(df, task, weights["data_sufficiency"]),
        check_leakage_validation(df, target, task, weights["leakage_validation"]),
    ]

    applicable = [d for d in dims if d.applicable and d.quality is not None]
    total_weight = sum(d.weight for d in applicable)
    if total_weight > 0:
        overall = 100.0 * sum(d.quality * d.weight for d in applicable) / total_weight
    else:
        overall = None

    all_checks = [c for d in dims for c in d.checks]
    coverage = {
        "total_checks": len(all_checks),
        "critical": sum(1 for c in all_checks if c.status == "critical"),
        "warnings": sum(1 for c in all_checks if c.status == "warning"),
        "passed": sum(1 for c in all_checks if c.status == "pass"),
        "not_applicable_dimensions": [d.name for d in dims if not d.applicable],
    }

    return AssessmentResult(
        task=task,
        target=target,
        overall_score=round(overall, 1) if overall is not None else None,
        dimensions=dims,
        coverage=coverage,
        engine_version=ENGINE_VERSION,
        scoring_config_id=DEFAULT_CONFIG_ID,
        generated_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        weights=weights,
    )
