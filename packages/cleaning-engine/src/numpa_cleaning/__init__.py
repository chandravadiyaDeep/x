"""
numpa_cleaning — NUMPA's Smart Data Cleaning engine.

A library of reusable, configurable preprocessing operations plus a
pipeline executor that records exactly what changed. Independent of
the website, API, and readiness engine.
"""

from .execution.pipeline import PipelineStep, run_pipeline

__all__ = ["PipelineStep", "run_pipeline"]
