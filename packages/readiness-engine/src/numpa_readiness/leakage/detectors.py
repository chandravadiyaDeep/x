"""
Leakage heuristics.

Important: these are heuristics, not proof. NUMPA must never claim a
dataset is guaranteed leakage-free — only surface confirmed / suspected
/ unknown signals for human review. Semantic leakage (a feature that is
only wrong because of what it *means* in the real world) cannot be
detected from data alone.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..checks import CheckResult, DimensionResult

NEAR_PERFECT_CORRELATION = 0.98


def check_leakage_validation(
    df: pd.DataFrame, target: str | None, task: str, weight: float
) -> DimensionResult:
    checks: list[CheckResult] = []

    if task == "clustering" or not target or target not in df.columns:
        checks.append(
            CheckResult(
                id="leakage.not_applicable",
                dimension="leakage_validation",
                title="Leakage checks not applicable",
                description="No target column is used for this task, so target-leakage checks don't apply.",
                status="pass",
                category="not_applicable",
                measurement={},
            )
        )
        return DimensionResult(
            name="leakage_validation", quality=1.0, weight=weight, applicable=True, checks=checks
        )

    quality = 1.0
    numeric_df = df.select_dtypes(include=[np.number])

    if target in numeric_df.columns and numeric_df.shape[1] > 1:
        correlations = numeric_df.corr(numeric_only=True)[target].drop(labels=[target], errors="ignore")
        suspicious = correlations[correlations.abs() > NEAR_PERFECT_CORRELATION]
        for col, corr in suspicious.items():
            checks.append(
                CheckResult(
                    id=f"leakage.near_perfect_correlation.{col}",
                    dimension="leakage_validation",
                    title=f"'{col}' is suspiciously correlated with the target",
                    description=(
                        f"Correlation of {corr:.3f} with '{target}' suggests this feature may "
                        "encode the target directly, or only become known after the outcome. "
                        "Review whether it would be available at prediction time."
                    ),
                    status="critical",
                    category="suspected",
                    measurement={"column": col, "correlation": float(corr)},
                )
            )
            quality = min(quality, 0.35)

    # Heuristic: any datetime-like column other than an explicit time index
    # is flagged as worth reviewing for temporal leakage.
    datetime_like_cols = [
        c
        for c in df.columns
        if c != target
        and (pd.api.types.is_datetime64_any_dtype(df[c]) or "date" in c.lower() or "time" in c.lower())
    ]
    for col in datetime_like_cols:
        checks.append(
            CheckResult(
                id=f"leakage.temporal_review.{col}",
                dimension="leakage_validation",
                title=f"'{col}' should be reviewed for temporal leakage",
                description=(
                    "This column looks time-related. Confirm it reflects information "
                    "available strictly before the prediction point."
                ),
                status="warning",
                category="suspected",
                measurement={"column": col},
            )
        )
        quality = min(quality, 0.75)

    if not checks:
        checks.append(
            CheckResult(
                id="leakage.overall",
                dimension="leakage_validation",
                title="No obvious leakage signals detected",
                description=(
                    "No near-perfect target correlations or timestamp-like columns were found. "
                    "This does not rule out semantic leakage that requires domain knowledge to catch."
                ),
                status="pass",
                category="unknown",
                measurement={},
            )
        )

    return DimensionResult(name="leakage_validation", quality=quality, weight=weight, applicable=True, checks=checks)
