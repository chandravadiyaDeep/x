from __future__ import annotations

import pandas as pd


def rename_columns(df: pd.DataFrame, params: dict) -> tuple[pd.DataFrame, dict]:
    """
    params:
      mapping: dict[str, str] — old column name -> new column name
    """
    mapping = params.get("mapping", {})
    valid_mapping = {k: v for k, v in mapping.items() if k in df.columns}
    df = df.rename(columns=valid_mapping)

    skipped = [k for k in mapping if k not in valid_mapping]
    warnings = [f"Column(s) not found, skipped: {', '.join(skipped)}"] if skipped else []

    return df, {
        "summary": f"Renamed {len(valid_mapping)} column(s)",
        "measurements": {"renamed": valid_mapping},
        "warnings": warnings,
    }
