from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    filename: Mapped[str] = mapped_column(String)
    storage_path: Mapped[str] = mapped_column(String)
    n_rows: Mapped[int] = mapped_column(Integer)
    n_cols: Mapped[int] = mapped_column(Integer)
    columns: Mapped[list] = mapped_column(JSON)
    dtypes: Mapped[dict] = mapped_column(JSON)
    uploaded_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)

    assessments: Mapped[list["Assessment"]] = relationship(back_populates="dataset")
    pipeline_executions: Mapped[list["PipelineExecution"]] = relationship(back_populates="dataset")


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    dataset_id: Mapped[str] = mapped_column(ForeignKey("datasets.id"))
    stage: Mapped[str] = mapped_column(String)  # "initial" | "final"
    task: Mapped[str] = mapped_column(String)
    target: Mapped[str | None] = mapped_column(String, nullable=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    result_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)

    dataset: Mapped["Dataset"] = relationship(back_populates="assessments")


class PipelineExecution(Base):
    __tablename__ = "pipeline_executions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    dataset_id: Mapped[str] = mapped_column(ForeignKey("datasets.id"))
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    steps_json: Mapped[list] = mapped_column(JSON)
    result_json: Mapped[dict] = mapped_column(JSON)
    cleaned_storage_path: Mapped[str] = mapped_column(String)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)

    dataset: Mapped["Dataset"] = relationship(back_populates="pipeline_executions")
