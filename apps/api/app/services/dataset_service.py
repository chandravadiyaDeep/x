from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.core.config import settings


def load_dataframe(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in (".csv", ".txt"):
        return pd.read_csv(path)
    if path.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")


def dataset_dir(dataset_id: str) -> Path:
    d = settings.STORAGE_DIR / dataset_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def original_path(dataset_id: str, filename: str) -> Path:
    return dataset_dir(dataset_id) / f"original{Path(filename).suffix}"


def cleaned_path(dataset_id: str, execution_id: str) -> Path:
    return dataset_dir(dataset_id) / f"cleaned_{execution_id}.csv"


def build_overview(df: pd.DataFrame) -> dict:
    missing = df.isna().sum()
    dtypes = df.dtypes.astype(str).to_dict()

    return {
        "n_rows": int(df.shape[0]),
        "n_columns": int(df.shape[1]),
        "columns": list(df.columns),
        "dtypes": dtypes,
        "missing_by_column": {c: int(v) for c, v in missing.items() if v > 0},
        "missing_ratio": float(df.isna().sum().sum() / (df.shape[0] * df.shape[1])) if df.size else 0.0,
        "duplicate_rows": int(df.duplicated().sum()),
        "preview": df.head(10).where(pd.notnull(df), None).to_dict(orient="records"),
        "numeric_summary": {
            col: {
                "mean": float(df[col].mean()) if df[col].notna().any() else None,
                "std": float(df[col].std()) if df[col].notna().any() else None,
                "min": float(df[col].min()) if df[col].notna().any() else None,
                "max": float(df[col].max()) if df[col].notna().any() else None,
            }
            for col in df.select_dtypes(include="number").columns
        },
    }
