from __future__ import annotations

import pandas as pd


def remove_duplicates(df: pd.DataFrame, params: dict) -> tuple[pd.DataFrame, dict]:
    """
    params:
      subset: list[str] | None — columns to consider (default: all columns)
      keep: "first" | "last" (default "first")
    """
    subset = params.get("subset")
    keep = params.get("keep", "first")

    before = len(df)
    df = df.drop_duplicates(subset=subset, keep=keep).reset_index(drop=True)
    removed = before - len(df)

    warnings = []
    if removed > 0:
        warnings.append(f"{removed} row(s) were permanently removed by this step.")

    return df, {
        "summary": f"Removed {removed} duplicate row(s)",
        "measurements": {"removed_rows": removed, "remaining_rows": len(df)},
        "warnings": warnings,
    }
