"""
numpa_readiness — NUMPA's ML Readiness Assessment engine.

Deterministic, explainable, task-aware scoring for whether a dataset
is ready for a given machine-learning task. This package has no
dependency on the website, API, or cleaning engine — it is a pure
Python library over pandas DataFrames.
"""

from .scoring.engine import assess
from .scoring.config import DEFAULT_WEIGHTS, ENGINE_VERSION

__all__ = ["assess", "DEFAULT_WEIGHTS", "ENGINE_VERSION"]
