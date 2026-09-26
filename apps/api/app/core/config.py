from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # apps/api/


class Settings:
    """
    NOTE on Supabase: the approved architecture uses Supabase for auth,
    metadata, and authorized storage. No Supabase project/credentials
    exist yet for this repo, so local development uses SQLite + local
    disk storage instead, behind the same repository interfaces
    (see app/repositories/). Swapping in Supabase later means
    implementing those interfaces against Supabase — not rewriting the
    routes or services.
    """

    CORS_ORIGINS: list[str] = os.getenv("NUMPA_CORS_ORIGINS", "http://localhost:3000").split(",")
    STORAGE_DIR: Path = Path(os.getenv("NUMPA_STORAGE_DIR", BASE_DIR / "storage" / "datasets"))
    DATABASE_URL: str = os.getenv("NUMPA_DATABASE_URL", f"sqlite:///{BASE_DIR / 'storage' / 'numpa.db'}")
    MAX_UPLOAD_MB: int = int(os.getenv("NUMPA_MAX_UPLOAD_MB", "50"))


settings = Settings()
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
