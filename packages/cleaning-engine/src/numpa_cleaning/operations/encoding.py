from __future__ import annotations

import pandas as pd


def one_hot_encode(df: pd.DataFrame, params: dict) -> tuple[pd.DataFrame, dict]:
    """
    params:
      columns: list[str] — categorical columns to encode
      drop_first: bool (default False)
      max_categories: int — safety cap; columns with more distinct values are skipped
    """
    df = df.copy()
    columns = params.get("columns", [])
    drop_first = params.get("drop_first", False)
    max_categories = params.get("max_categories", 50)

    encoded_cols: list[str] = []
    skipped: list[str] = []
    before_cols = set(df.columns)

    valid_columns = []
    for col in columns:
        if col not in df.columns:
            continue
        if df[col].nunique(dropna=True) > max_categories:
            skipped.append(col)
            continue
        valid_columns.append(col)

    if valid_columns:
        df = pd.get_dummies(df, columns=valid_columns, drop_first=drop_first)
        encoded_cols = [c for c in df.columns if c not in before_cols]

    warnings = []
    if skipped:
        warnings.append(
            f"Skipped {len(skipped)} column(s) exceeding {max_categories} categories: {', '.join(skipped)}"
        )

    return df, {
        "summary": f"One-hot encoded {len(valid_columns)} column(s), adding {len(encoded_cols)} column(s)",
        "measurements": {
            "encoded_source_columns": valid_columns,
            "new_columns": encoded_cols,
            "skipped_columns": skipped,
        },
        "warnings": warnings,
    }
