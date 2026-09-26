"""
Task-dependent checks: feature suitability, target suitability, data sufficiency.

These require knowing the ML task and (for supervised tasks) the target column.
"""

from __future__ import annotations

import pandas as pd

from . import CheckResult, DimensionResult

MIN_ROWS_BY_TASK = {
    "classification": 100,
    "regression": 100,
    "forecasting": 60,
    "clustering": 50,
}


def check_feature_suitability(df: pd.DataFrame, target: str | None, weight: float) -> DimensionResult:
    checks: list[CheckResult] = []
    feature_cols = [c for c in df.columns if c != target]

    constant_cols = [c for c in feature_cols if df[c].nunique(dropna=True) <= 1]
    high_cardinality_cols = [
        c
        for c in feature_cols
        if df[c].dtype == object and df[c].nunique(dropna=True) > 0.9 * len(df) and len(df) > 20
    ]

    if constant_cols:
        checks.append(
            CheckResult(
                id="feature.constant_columns",
                dimension="feature_suitability",
                title=f"{len(constant_cols)} column(s) have a single constant value",
                description=f"Columns with no variation carry no signal: {', '.join(constant_cols[:5])}.",
                status="warning",
                category="confirmed",
                measurement={"columns": constant_cols},
            )
        )
    if high_cardinality_cols:
        checks.append(
            CheckResult(
                id="feature.high_cardinality",
                dimension="feature_suitability",
                title=f"{len(high_cardinality_cols)} column(s) look like identifiers",
                description=(
                    "Near-unique text columns (e.g. IDs, free text) usually need encoding or "
                    "removal before modeling: " + ", ".join(high_cardinality_cols[:5])
                ),
                status="warning",
                category="suspected",
                measurement={"columns": high_cardinality_cols},
            )
        )
    if not constant_cols and not high_cardinality_cols:
        checks.append(
            CheckResult(
                id="feature.overall",
                dimension="feature_suitability",
                title="Features look usable",
                description="No constant or identifier-like columns detected among the features.",
                status="pass",
                category="confirmed",
                measurement={},
            )
        )

    penalty = (len(constant_cols) + len(high_cardinality_cols)) / max(len(feature_cols), 1)
    quality = max(0.0, 1.0 - penalty)
    return DimensionResult(
        name="feature_suitability", quality=quality, weight=weight, applicable=True, checks=checks
    )


def check_target_suitability(
    df: pd.DataFrame, target: str | None, task: str, weight: float
) -> DimensionResult:
    checks: list[CheckResult] = []

    if task == "clustering":
        return DimensionResult(name="target_suitability", quality=None, weight=weight, applicable=False, checks=[])

    if not target or target not in df.columns:
        checks.append(
            CheckResult(
                id="target.missing_selection",
                dimension="target_suitability",
                title="No target column selected",
                description=f"A '{task}' assessment needs a target column to evaluate properly.",
                status="critical",
                category="unknown",
                measurement={},
            )
        )
        return DimensionResult(name="target_suitability", quality=None, weight=weight, applicable=False, checks=checks)

    target_series = df[target]
    missing_ratio = target_series.isna().mean()

    if missing_ratio > 0:
        checks.append(
            CheckResult(
                id="target.missing_labels",
                dimension="target_suitability",
                title=f"Target has {missing_ratio * 100:.1f}% missing values",
                description="Rows without a label can't be used for supervised training.",
                status="critical" if missing_ratio > 0.2 else "warning",
                category="confirmed",
                measurement={"missing_ratio": float(missing_ratio)},
            )
        )

    quality = max(0.0, 1.0 - missing_ratio * 1.5)

    if task == "classification":
        counts = target_series.value_counts(normalize=True, dropna=True)
        if len(counts) < 2:
            checks.append(
                CheckResult(
                    id="target.single_class",
                    dimension="target_suitability",
                    title="Target has only one class present",
                    description="Classification requires at least two distinct classes.",
                    status="critical",
                    category="confirmed",
                    measurement={"class_count": int(len(counts))},
                )
            )
            quality = 0.0
        elif counts.min() < 0.05:
            checks.append(
                CheckResult(
                    id="target.class_imbalance",
                    dimension="target_suitability",
                    title="Severe class imbalance detected",
                    description=(
                        f"Minority class makes up {counts.min() * 100:.1f}% of records. "
                        "Consider stratified sampling or class weighting."
                    ),
                    status="warning",
                    category="confirmed",
                    measurement={"minority_share": float(counts.min())},
                )
            )
            quality = min(quality, 0.7)
    elif task == "regression":
        numeric_ok = pd.to_numeric(target_series, errors="coerce").notna().mean()
        if numeric_ok < 0.95:
            checks.append(
                CheckResult(
                    id="target.non_numeric",
                    dimension="target_suitability",
                    title="Target is not consistently numeric",
                    description="Regression requires a continuous numeric target.",
                    status="critical",
                    category="confirmed",
                    measurement={"numeric_ratio": float(numeric_ok)},
                )
            )
            quality = min(quality, 0.2)

    if not checks:
        checks.append(
            CheckResult(
                id="target.overall",
                dimension="target_suitability",
                title="Target column is valid and complete",
                description=f"'{target}' has no missing values and both classes are represented."
                if task == "classification"
                else f"'{target}' is complete and numeric.",
                status="pass",
                category="confirmed",
                measurement={},
            )
        )

    return DimensionResult(name="target_suitability", quality=quality, weight=weight, applicable=True, checks=checks)


def check_data_sufficiency(df: pd.DataFrame, task: str, weight: float) -> DimensionResult:
    checks: list[CheckResult] = []
    n_rows = len(df)
    min_rows = MIN_ROWS_BY_TASK.get(task, 100)

    if n_rows < min_rows:
        checks.append(
            CheckResult(
                id="sufficiency.row_count",
                dimension="data_sufficiency",
                title=f"Only {n_rows} rows available",
                description=(
                    f"A reasonable starting point for {task} is roughly {min_rows}+ rows; "
                    "fewer rows increase the risk of an unreliable model."
                ),
                status="warning" if n_rows > min_rows * 0.4 else "critical",
                category="confirmed",
                measurement={"row_count": n_rows, "recommended_minimum": min_rows},
            )
        )
        quality = max(0.0, n_rows / min_rows)
    else:
        checks.append(
            CheckResult(
                id="sufficiency.row_count",
                dimension="data_sufficiency",
                title="Row count looks adequate",
                description=f"{n_rows} rows meets the rough minimum for {task}.",
                status="pass",
                category="confirmed",
                measurement={"row_count": n_rows},
            )
        )
        quality = 1.0

    return DimensionResult(name="data_sufficiency", quality=quality, weight=weight, applicable=True, checks=checks)
