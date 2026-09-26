"""
Versioned scoring configuration.

Weights here are the provisional defaults from the NUMPA product spec
(September 2026). They are design hypotheses, not validated constants —
callers can override them per-assessment (this is what the future
Custom Model Studio will do).
"""

from __future__ import annotations

ENGINE_VERSION = "0.1.0"

DEFAULT_CONFIG_ID = "default-v1"

# Seven scoring dimensions and their default weights (must sum to 1.0
# across whatever subset is applicable to a given task).
DEFAULT_WEIGHTS: dict[str, float] = {
    "completeness": 0.20,
    "validity_consistency": 0.15,
    "record_integrity": 0.10,
    "feature_suitability": 0.15,
    "target_suitability": 0.15,
    "data_sufficiency": 0.10,
    "leakage_validation": 0.15,
}

SUPPORTED_TASKS = ("classification", "regression", "forecasting", "clustering")

# Dimensions that don't apply when there is no target column (clustering).
NO_TARGET_DIMENSIONS = {"target_suitability"}
