from __future__ import annotations

import pandas as pd


def impute_missing_values(df: pd.DataFrame, params: dict) -> tuple[pd.DataFrame, dict]:
    """
    params:
      columns: list[str] — columns to impute (default: all columns with missing values)
      strategy: "mean" | "median" | "mode" | "constant" (default "median")
      fill_value: used when strategy == "constant"
    """
    df = df.copy()
    columns = params.get("columns") or df.columns[df.isna().any()].tolist()
    strategy = params.get("strategy", "median")
    fill_value = params.get("fill_value")

    affected: dict[str, int] = {}
    for col in columns:
        if col not in df.columns:
            continue
        n_missing = int(df[col].isna().sum())
        if n_missing == 0:
            continue

        if strategy == "mean":
            value = df[col].mean()
        elif strategy == "median":
            value = df[col].median()
        elif strategy == "mode":
            mode = df[col].mode(dropna=True)
            value = mode.iloc[0] if not mode.empty else None
        elif strategy == "constant":
            value = fill_value
        else:
            raise ValueError(f"Unknown imputation strategy: {strategy}")

        df[col] = df[col].fillna(value)
        affected[col] = n_missing

    return df, {
        "summary": f"Imputed missing values in {len(affected)} column(s) using '{strategy}'",
        "measurements": {"strategy": strategy, "affected_columns": affected},
        "warnings": [],
    }
