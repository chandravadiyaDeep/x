# NUMPA — Project Knowledge & Product Specification

This is the approved product/architecture document this scaffold was
built from (September 2026). It distinguishes confirmed decisions from
provisional proposals — see its final section for how to interpret it.

For a summary of what in this repo is actually implemented versus still
a placeholder relative to this spec, see the root `README.md`.

---

## 1. Project identity and vision

NUMPA is a SaaS platform designed to help data professionals prepare
datasets for machine learning. Its core purpose is to reduce the time
analysts and ML practitioners spend diagnosing data problems, cleaning
datasets, and determining whether data is suitable for a particular
machine-learning task.

Two core features:
- **Smart Data Cleaning** — a configurable, user-controlled system for
  identifying and correcting dataset problems through reusable
  preprocessing pipelines.
- **ML Readiness Assessment** — an explainable, task-dependent system
  for evaluating how suitable a dataset is for a specified
  machine-learning task and intended algorithm.

## 2. Four-stage workflow

1. **Upload dataset** — inspect the original file, immutable original
   preserved.
2. **Initial ML readiness** — assess the data for the chosen task,
   identify problems.
3. **Smart data cleaning** — review, configure, and execute
   preprocessing.
4. **Final ML readiness** — reassess and compare before vs. after.

PDF reporting at every stage, plus cleaned-dataset export.

## 3. Four supported ML tasks

Classification, Regression, Time-series forecasting, Clustering — each
with its own relevant checks (see `packages/readiness-engine`).

## 4. Seven scoring dimensions (provisional weights)

| Dimension | Weight | Purpose |
|---|---|---|
| Completeness | 20% | Missing values and missing required information |
| Validity & consistency | 15% | Invalid values, inconsistent types, format problems |
| Record integrity | 10% | Duplicate and structurally problematic records |
| Feature suitability | 15% | Relevance and usability of input features |
| Target suitability | 15% | Target availability, validity, task compatibility |
| Data sufficiency | 10% | Whether available data is adequate for the task |
| Leakage & validation | 15% | Leakage risks and validation strategy fit |

`score = 100 × (Σ w_i · q_i) / (Σ w_i)` over applicable, evaluated
dimensions. An unevaluated dimension is excluded, not defaulted to
neutral. Critical warnings stay visible regardless of the aggregate
score.

## 5. Architecture

Modular monorepo: Next.js frontend, FastAPI backend, independently
maintained Python engines (readiness, cleaning, report), Supabase for
auth/DB/authorized storage (not yet connected in this scaffold — see
README).

## 6. Confirmed vs. open decisions

**Confirmed:** two core features, four-stage workflow, four ML tasks,
explainable/configurable scoring, leakage prevention required,
user-controlled cleaning, PDF export at every stage, Next.js frontend,
FastAPI + modular Python engines, Supabase auth, Vercel frontend
hosting.

**Open:** initial scoring weights (provisional), production Python
hosting (to be evaluated), final dataset-processing privacy model,
final pricing and payment provider, exact readiness thresholds, timeline
for API/Zapier/white-label.

## 7. What this scaffold does not include yet

Per the spec's own guiding principle — build the two core features to a
high standard before expanding into adjacent functionality — this
scaffold does not yet include: authentication, Supabase, team
workspaces, Custom Model Studio, saved-pipeline persistence, Zapier,
white-label embedding, or billing. Static (non-functional) mockups of
those pages were built in an earlier design pass; none are wired to
real data or logic.
