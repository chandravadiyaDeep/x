 #NUMPA

Smart Data Cleaning + ML Readiness Assessment, in one workflow.

This is a working full-stack scaffold: a FastAPI backend with two real,
tested Python engines (readiness scoring and data cleaning), and a
Next.js frontend wired to it with actual network calls — no mocked
data anywhere in the app code.

## What's real vs. what's a placeholder

**Fully implemented and tested:**
- `packages/readiness-engine` — deterministic scoring for classification
  and regression across all 7 dimensions from the spec (completeness,
  validity, record integrity, feature suitability, target suitability,
  data sufficiency, leakage/validation), plus heuristic leakage detection
  (near-perfect target correlation, timestamp-column review flags).
- `packages/cleaning-engine` — 8 working operations (impute, dedupe,
  one-hot encode, standard scale, IQR outlier removal, dtype conversion,
  text cleaning, column rename) and a pipeline executor with full audit
  history.
- `apps/api` — FastAPI backend: dataset upload/parsing (CSV/Excel),
  readiness assessment, cleaning pipeline execution, PDF report
  generation. All backed by SQLite + local disk (see note below).
- `apps/web` — Next.js/TypeScript/Tailwind frontend: dashboard (lists
  real uploaded datasets), upload page, and a dataset workflow page that
  runs the actual 4-stage flow (overview → initial readiness → cleaning
  → final readiness) against the live API.

**Stubbed / not yet built** (per the project's own roadmap — these come
after the two core features are solid):
- Forecasting and clustering readiness scoring return the same
  structural checks as classification/regression but haven't been
  tuned with task-specific logic yet (e.g. no chronological-gap checks
  for forecasting).
- Auth, Supabase, team workspaces, Custom Model Studio, Zapier,
  white-label embedding, billing — none of these have real backing
  services connected. Building them without real credentials would
  just be fake plumbing, so they're left out rather than faked.
- The cleaning pipeline builder UI uses a plain JSON editor for step
  parameters rather than a dedicated per-operation form — functional,
  not polished.

## Important note on Supabase

The approved architecture (see `docs/`) uses Supabase for auth, metadata,
and storage. No Supabase project or credentials exist yet, so this
scaffold uses **SQLite + local disk** behind the same repository
interfaces (`apps/api/app/models.py`, `apps/api/app/services/`). When
you're ready to connect Supabase, you're implementing against those
same interfaces — not rewriting the routes.

## Project structure

```
apps/
  web/        Next.js frontend (TypeScript, Tailwind)
  api/        FastAPI backend
packages/
  readiness-engine/   numpa_readiness — standalone Python package
  cleaning-engine/    numpa_cleaning — standalone Python package
  report-engine/      (placeholder — PDF generation currently lives
                       in apps/api/app/services/report_service.py;
                       move here if it needs to be shared elsewhere)
database/     (placeholder for migrations once a real DB is chosen)
docs/         Project knowledge doc this scaffold was built from
```

## Running it locally

### 1. Backend (FastAPI)

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # also installs the two local engines, editable
cp .env.example .env              # defaults work as-is for local dev
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive API docs.

Run the test suite:

```bash
# from apps/api, with the venv active
pytest

# each engine also has its own tests:
cd ../../packages/readiness-engine && pytest
cd ../cleaning-engine && pytest
```

### 2. Frontend (Next.js)

```bash
cd apps/web
npm install
cp .env.example .env.local        # points at http://localhost:8000 by default
npm run dev
```

Visit `http://localhost:3000`.

### 3. Try the full workflow

1. Go to `/upload`, drop in a CSV (a churn/customer dataset with a
   binary target works well for a first test).
2. You'll land on the dataset's workflow page. Pick a task
   (`classification` is a safe default) and a target column, then
   **Run initial assessment** — this calls the real readiness engine.
3. Add cleaning steps (e.g. `impute_missing_values`, `remove_duplicates`)
   and **Run pipeline** — this calls the real cleaning engine.
4. **Re-assess cleaned dataset** to see the final score and compare it
   to the initial one.
5. Download the PDF reports from the Reports section.

## Design system

The frontend and the standalone HTML mockups built earlier share one
visual language: deep navy background (`#080d17`), blue (`#4f8cff`) /
cyan (`#31d5c8`) accents, `Space Grotesk` for headings, `IBM Plex Sans`
for body text, `IBM Plex Mono` for numbers and code. Tokens live in
`apps/web/src/app/globals.css`.

## What to do next

Roughly in the order the project spec's own roadmap suggests:

1. Tune forecasting/clustering-specific checks in the readiness engine.
2. Add auth (Supabase or otherwise) and swap the SQLite/local-disk
   repository implementations for real ones.
3. Replace the JSON-editor cleaning step UI with proper per-operation
   forms (column pickers, strategy dropdowns).
4. Add the Custom Model Studio, saved pipelines persistence UI, team
   workspaces, and integrations — all currently just static mockups
   from the earlier design pass, not wired to real data.
