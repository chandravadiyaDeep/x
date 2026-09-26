from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Status = Literal["pass", "warning", "critical"]
Category = Literal["confirmed", "suspected", "unknown", "not_applicable"]


@dataclass
class CheckResult:
    """A single, explainable check outcome."""

    id: str
    dimension: str
    title: str
    description: str
    status: Status
    category: Category
    measurement: dict = field(default_factory=dict)


@dataclass
class DimensionResult:
    """The aggregated outcome for one scoring dimension."""

    name: str
    quality: float | None  # 0.0-1.0, or None if the dimension could not be evaluated
    weight: float
    applicable: bool
    checks: list[CheckResult] = field(default_factory=list)
