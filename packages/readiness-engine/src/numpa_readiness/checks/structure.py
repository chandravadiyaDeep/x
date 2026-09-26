"""
Structural checks: completeness, validity & consistency, record integrity.

These checks look at the dataset on its own, independent of the ML task.
"""

from __future__ import annotations

import pandas as pd

from . import CheckResult, DimensionResult


def check_completeness(df: pd.DataFrame, weight: float) -> DimensionResult:
    checks: list[CheckResult] = []
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = int(df.isna().sum().sum())
    missing_ratio = missing_cells / total_cells if total_cells else 0.0

    cols_with_missing = df.columns[df.isna().any()].tolist()
    if cols_with_missing:
        worst = df[cols_with_missing].isna().mean().sort_values(ascending=False)
        status = "critical" if missing_ratio > 0.3 else "warning" if missing_ratio > 0.05 else "pass"
        checks.append(
            CheckResult(
                id="completeness.missing_values",
                dimension="completeness",
                title=f"{len(cols_with_missing)} column(s) contain missing values",
                description=(
                    f"Worst column ('{worst.index[0]}') is "
                    f"{worst.iloc[0] * 100:.1f}% missing. Overall missingness is "
                    f"{missing_ratio * 100:.1f}% of all cells."
                ),
                status=status,
                category="confirmed",
                measurement={"missing_ratio": missing_ratio, "columns": cols_with_missing},
            )
        )
    else:
        checks.append(
            CheckResult(
                id="completeness.missing_values",
                dimension="completeness",
                title="No missing values detected",
                description="Every column is fully populated.",
                status="pass",
                category="confirmed",
                measurement={"missing_ratio": 0.0},
            )
        )

    quality = max(0.0, 1.0 - missing_ratio * 2)  # 15% missing overall -> 0.70 quality
    return DimensionResult(name="completeness", quality=quality, weight=weight, applicable=True, checks=checks)


def check_validity_consistency(df: pd.DataFrame, weight: float) -> DimensionResult:
    checks: list[CheckResult] = []
    issues = 0
    total_checked = 0

    for col in df.columns:
        series = df[col]
        total_checked += 1

        if series.dtype == object:
            # Mixed-type detection: does the column look numeric but is stored as text?
            non_null = series.dropna()
            if len(non_null) == 0:
                continue
            numeric_like = pd.to_numeric(non_null, errors="coerce").notna().mean()
            if 0.5 < numeric_like < 1.0:
                issues += 1
                checks.append(
                    CheckResult(
                        id=f"validity.mixed_type.{col}",
                        dimension="validity_consistency",
                        title=f"Column '{col}' has inconsistent types",
                        description=(
                            f"{numeric_like * 100:.0f}% of values look numeric, "
                            "the rest do not parse as numbers."
                        ),
                        status="warning",
                        category="confirmed",
                        measurement={"numeric_like_ratio": float(numeric_like)},
                    )
                )

    if issues == 0:
        checks.append(
            CheckResult(
                id="validity.overall",
                dimension="validity_consistency",
                title="No type or format inconsistencies detected",
                description="All columns have a consistent, parseable format.",
                status="pass",
                category="confirmed",
                measurement={},
            )
        )

    quality = max(0.0, 1.0 - (issues / max(total_checked, 1)) * 1.5)
    return DimensionResult(
        name="validity_consistency", quality=quality, weight=weight, applicable=True, checks=checks
    )


def check_record_integrity(df: pd.DataFrame, weight: float) -> DimensionResult:
    checks: list[CheckResult] = []
    dup_count = int(df.duplicated().sum())
    dup_ratio = dup_count / len(df) if len(df) else 0.0

    if dup_count > 0:
        status = "critical" if dup_ratio > 0.1 else "warning"
        checks.append(
            CheckResult(
                id="integrity.duplicates",
                dimension="record_integrity",
                title=f"{dup_count} duplicate record(s) found",
                description=f"{dup_ratio * 100:.1f}% of rows are exact duplicates of another row.",
                status=status,
                category="confirmed",
                measurement={"duplicate_count": dup_count, "duplicate_ratio": dup_ratio},
            )
        )
    else:
        checks.append(
            CheckResult(
                id="integrity.duplicates",
                dimension="record_integrity",
                title="No duplicate records found",
                description="Every row is unique.",
                status="pass",
                category="confirmed",
                measurement={"duplicate_count": 0},
            )
        )

    quality = max(0.0, 1.0 - dup_ratio * 2)
    return DimensionResult(name="record_integrity", quality=quality, weight=weight, applicable=True, checks=checks)
