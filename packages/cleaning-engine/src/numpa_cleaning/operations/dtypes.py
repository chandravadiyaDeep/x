from __future__ import annotations

import pandas as pd


def convert_dtype(df: pd.DataFrame, params: dict) -> tuple[pd.DataFrame, dict]:
    """
    params:
      columns: dict[str, str] — mapping of column name -> target dtype
        ("int", "float", "str", "category", "datetime", "bool")
    """
    df = df.copy()
    mapping = params.get("columns", {})
    converted: dict[str, str] = {}
    failed: dict[str, str] = {}

    dtype_map = {
        "int": "Int64",
        "float": "float64",
        "str": "string",
        "category": "category",
        "bool": "boolean",
    }

    for col, target_dtype in mapping.items():
        if col not in df.columns:
            continue
        try:
            if target_dtype == "datetime":
                df[col] = pd.to_datetime(df[col], errors="raise")
            elif target_dtype in ("int", "float"):
                df[col] = pd.to_numeric(df[col], errors="raise").astype(dtype_map[target_dtype])
            else:
                df[col] = df[col].astype(dtype_map.get(target_dtype, target_dtype))
            converted[col] = target_dtype
        except Exception as exc:  # noqa: BLE001 - surfaced to the user, not swallowed
            failed[col] = str(exc)

    warnings = [f"Could not convert '{c}': {msg}" for c, msg in failed.items()]

    return df, {
        "summary": f"Converted {len(converted)} column(s); {len(failed)} failed",
        "measurements": {"converted": converted, "failed": failed},
        "warnings": warnings,
    }
