from __future__ import annotations

import pandas as pd


def clean_text(df: pd.DataFrame, params: dict) -> tuple[pd.DataFrame, dict]:
    """
    params:
      columns: list[str] — text columns to clean
      lowercase: bool (default True)
      strip_whitespace: bool (default True)
      collapse_internal_whitespace: bool (default True)
    """
    df = df.copy()
    columns = params.get("columns", [])
    lowercase = params.get("lowercase", True)
    strip_whitespace = params.get("strip_whitespace", True)
    collapse_internal_whitespace = params.get("collapse_internal_whitespace", True)

    touched = []
    for col in columns:
        if col not in df.columns:
            continue
        series = df[col].astype("string")
        if strip_whitespace:
            series = series.str.strip()
        if collapse_internal_whitespace:
            series = series.str.replace(r"\s+", " ", regex=True)
        if lowercase:
            series = series.str.lower()
        df[col] = series
        touched.append(col)

    return df, {
        "summary": f"Cleaned text in {len(touched)} column(s)",
        "measurements": {"columns": touched},
        "warnings": [],
    }
