from __future__ import annotations

import numpy as np
import pandas as pd


def standard_scale(df: pd.DataFrame, params: dict) -> tuple[pd.DataFrame, dict]:
    """
    params:
      columns: list[str] — numeric columns to scale (default: all numeric columns)
      fit_row_mask: list[bool] | None — rows to fit the mean/std on (e.g. the training
        split). Leakage-safe preprocessing requires this for supervised ML prep; when
        omitted, the operation fits on the whole dataset and a warning is raised.
    """
    df = df.copy()
    columns = params.get("columns") or df.select_dtypes(include=[np.number]).columns.tolist()
    fit_row_mask = params.get("fit_row_mask")

    warnings = []
    fit_df = df
    if fit_row_mask is not None:
        mask = pd.Series(fit_row_mask, index=df.index[: len(fit_row_mask)])
        fit_df = df.loc[mask[mask].index]
    else:
        warnings.append(
            "No training-row mask supplied — scaling was fit on the full dataset. "
            "For leakage-safe supervised ML prep, fit only on the training split."
        )

    stats: dict[str, dict] = {}
    for col in columns:
        if col not in df.columns:
            continue
        mean = fit_df[col].mean()
        std = fit_df[col].std()
        std = std if std and std > 1e-9 else 1.0
        df[col] = (df[col] - mean) / std
        stats[col] = {"mean": float(mean), "std": float(std)}

    return df, {
        "summary": f"Standard-scaled {len(stats)} column(s)",
        "measurements": {"columns": stats},
        "warnings": warnings,
    }
