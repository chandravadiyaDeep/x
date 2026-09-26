from __future__ import annotations

import numpy as np
import pandas as pd


def remove_outliers_iqr(df: pd.DataFrame, params: dict) -> tuple[pd.DataFrame, dict]:
    """
    params:
      columns: list[str] — numeric columns to check (default: all numeric columns)
      multiplier: float — IQR multiplier for the fence (default 1.5)
    """
    columns = params.get("columns") or df.select_dtypes(include=[np.number]).columns.tolist()
    multiplier = params.get("multiplier", 1.5)

    before = len(df)
    keep_mask = pd.Series(True, index=df.index)
    bounds: dict[str, dict] = {}

    for col in columns:
        if col not in df.columns:
            continue
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - multiplier * iqr, q3 + multiplier * iqr
        bounds[col] = {"lower": float(lower), "upper": float(upper)}
        keep_mask &= df[col].between(lower, upper) | df[col].isna()

    df = df.loc[keep_mask].reset_index(drop=True)
    removed = before - len(df)

    warnings = []
    if removed > 0:
        warnings.append(f"{removed} row(s) were permanently removed as outliers.")

    return df, {
        "summary": f"Removed {removed} row(s) outside {multiplier}x IQR bounds",
        "measurements": {"removed_rows": removed, "bounds": bounds},
        "warnings": warnings,
    }
