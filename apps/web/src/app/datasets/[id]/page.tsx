"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  getDataset,
  runAssessment,
  listOperations,
  runCleaningPipeline,
  overviewReportUrl,
  assessmentReportUrl,
  type DatasetOverview,
  type AssessmentResult,
  type PipelineRunResult,
  type PipelineStepDef,
} from "@/lib/api";

const TASKS = ["classification", "regression", "forecasting", "clustering"];

const OPERATION_DEFAULT_PARAMS: Record<string, Record<string, unknown>> = {
  impute_missing_values: { strategy: "median" },
  remove_duplicates: {},
  one_hot_encode: { columns: [] },
  standard_scale: { columns: [] },
  remove_outliers_iqr: { columns: [], multiplier: 1.5 },
  convert_dtype: { columns: {} },
  clean_text: { columns: [] },
  rename_columns: { mapping: {} },
};

function statusBadgeClass(status: string) {
  if (status === "critical") return "badge badge-critical";
  if (status === "warning") return "badge badge-warning";
  return "badge badge-pass";
}

export default function DatasetWorkflowPage() {
  const params = useParams<{ id: string }>();
  const datasetId = params.id;

  const [dataset, setDataset] = useState<{ dataset_id: string; filename: string; overview: DatasetOverview } | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [task, setTask] = useState("classification");
  const [target, setTarget] = useState<string>("");
  const [initialAssessment, setInitialAssessment] = useState<AssessmentResult | null>(null);
  const [finalAssessment, setFinalAssessment] = useState<AssessmentResult | null>(null);
  const [assessing, setAssessing] = useState(false);
  const [assessError, setAssessError] = useState<string | null>(null);

  const [operations, setOperations] = useState<string[]>([]);
  const [steps, setSteps] = useState<PipelineStepDef[]>([]);
  const [pipelineResult, setPipelineResult] = useState<PipelineRunResult | null>(null);
  const [running, setRunning] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);

  useEffect(() => {
    getDataset(datasetId).then(setDataset).catch((e) => setLoadError(e.message));
    listOperations().then((r) => setOperations(r.operations)).catch(() => {});
  }, [datasetId]);

  async function handleAssess(stage: "initial" | "final") {
    setAssessing(true);
    setAssessError(null);
    try {
      const result = await runAssessment({
        dataset_id: datasetId,
        task,
        target: task === "clustering" ? null : target || null,
        stage,
      });
      if (stage === "initial") setInitialAssessment(result);
      else setFinalAssessment(result);
    } catch (e) {
      setAssessError(e instanceof Error ? e.message : "Assessment failed");
    } finally {
      setAssessing(false);
    }
  }

  function addStep(type: string) {
    const id = `${type}-${Date.now()}`;
    setSteps((prev) => [...prev, { id, type, params: structuredClone(OPERATION_DEFAULT_PARAMS[type] ?? {}) }]);
  }

  function updateStepParams(id: string, raw: string) {
    setSteps((prev) =>
      prev.map((s) => {
        if (s.id !== id) return s;
        try {
          return { ...s, params: JSON.parse(raw) };
        } catch {
          return s; // ignore invalid JSON while typing
        }
      })
    );
  }

  function removeStep(id: string) {
    setSteps((prev) => prev.filter((s) => s.id !== id));
  }

  async function handleRunPipeline() {
    setRunning(true);
    setRunError(null);
    try {
      const result = await runCleaningPipeline({ dataset_id: datasetId, name: "web pipeline", steps });
      setPipelineResult(result);
    } catch (e) {
      setRunError(e instanceof Error ? e.message : "Pipeline run failed");
    } finally {
      setRunning(false);
    }
  }

  if (loadError) {
    return (
      <div className="max-w-4xl mx-auto px-7 py-10">
        <div className="panel" style={{ borderColor: "var(--red)" }}>
          <p className="text-sm">Could not load dataset: {loadError}</p>
        </div>
      </div>
    );
  }

  if (!dataset) {
    return (
      <div className="max-w-4xl mx-auto px-7 py-10 text-sm" style={{ color: "var(--muted)" }}>
        Loading dataset…
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-7 py-10 flex flex-col gap-8">
      <div>
        <h1 className="text-2xl font-bold">{dataset.filename}</h1>
        <p className="text-sm mt-1" style={{ color: "var(--muted)" }}>
          {dataset.overview.n_rows} rows · {dataset.overview.n_columns} columns · {dataset.overview.duplicate_rows} duplicates
        </p>
      </div>

      {/* Stage 2: Initial readiness */}
      <section className="panel">
        <h2 className="text-base font-semibold mb-4">Readiness assessment</h2>
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div>
            <label className="text-xs block mb-1" style={{ color: "var(--muted)" }}>
              Task
            </label>
            <select className="select" value={task} onChange={(e) => setTask(e.target.value)}>
              {TASKS.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
          {task !== "clustering" && (
            <div>
              <label className="text-xs block mb-1" style={{ color: "var(--muted)" }}>
                Target column
              </label>
              <select className="select" value={target} onChange={(e) => setTarget(e.target.value)}>
                <option value="">Select a column…</option>
                {dataset.overview.columns.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
        <button className="btn btn-primary" disabled={assessing} onClick={() => handleAssess("initial")}>
          {assessing ? "Assessing…" : "Run initial assessment"}
        </button>
        {assessError && (
          <p className="text-sm mt-3" style={{ color: "var(--red)" }}>
            {assessError}
          </p>
        )}
        {initialAssessment && <AssessmentView result={initialAssessment} />}
      </section>

      {/* Stage 3: Cleaning */}
      <section className="panel">
        <h2 className="text-base font-semibold mb-1">Cleaning pipeline</h2>
        <p className="text-xs mb-4" style={{ color: "var(--muted)" }}>
          Add steps, edit their parameters as JSON, then run. The original dataset is never modified.
        </p>

        <div className="flex flex-wrap gap-2 mb-4">
          {operations.map((op) => (
            <button key={op} className="btn btn-ghost text-xs" onClick={() => addStep(op)}>
              + {op}
            </button>
          ))}
        </div>

        <div className="flex flex-col gap-3 mb-4">
          {steps.map((step, i) => (
            <div key={step.id} className="p-3 rounded-lg" style={{ background: "var(--surface-2)", border: "1px solid var(--line)" }}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium mono">
                  {i + 1}. {step.type}
                </span>
                <button className="text-xs" style={{ color: "var(--red)" }} onClick={() => removeStep(step.id)}>
                  Remove
                </button>
              </div>
              <textarea
                className="input mono text-xs"
                rows={3}
                defaultValue={JSON.stringify(step.params, null, 2)}
                onBlur={(e) => updateStepParams(step.id, e.target.value)}
              />
            </div>
          ))}
          {steps.length === 0 && (
            <p className="text-xs" style={{ color: "var(--muted)" }}>
              No steps yet — add one from the operations above.
            </p>
          )}
        </div>

        <button className="btn btn-primary" disabled={running || steps.length === 0} onClick={handleRunPipeline}>
          {running ? "Running…" : "Run pipeline"}
        </button>
        {runError && (
          <p className="text-sm mt-3" style={{ color: "var(--red)" }}>
            {runError}
          </p>
        )}

        {pipelineResult && (
          <div className="mt-5">
            <p className="text-sm mb-3">
              {pipelineResult.original_rows} → {pipelineResult.final_rows} rows after {pipelineResult.steps.length} step(s)
            </p>
            <div className="flex flex-col gap-2">
              {pipelineResult.steps.map((s) => (
                <div key={s.step_id} className="text-sm p-2 rounded" style={{ background: "var(--surface-2)" }}>
                  <span className="mono text-xs" style={{ color: "var(--cyan)" }}>
                    {s.type}
                  </span>{" "}
                  — {s.summary}
                  {s.warnings.length > 0 && (
                    <div style={{ color: "var(--amber)" }} className="text-xs mt-1">
                      {s.warnings.join(" ")}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* Stage 4: Final comparison */}
      {pipelineResult && (
        <section className="panel">
          <h2 className="text-base font-semibold mb-4">Final readiness</h2>
          <button className="btn btn-primary" disabled={assessing} onClick={() => handleAssess("final")}>
            {assessing ? "Assessing…" : "Re-assess cleaned dataset"}
          </button>
          {finalAssessment && <AssessmentView result={finalAssessment} />}
          {initialAssessment && finalAssessment && initialAssessment.overall_score !== null && finalAssessment.overall_score !== null && (
            <p className="text-sm mt-4">
              Score changed from <span className="mono">{initialAssessment.overall_score}</span> to{" "}
              <span className="mono" style={{ color: "var(--cyan)" }}>
                {finalAssessment.overall_score}
              </span>
            </p>
          )}
        </section>
      )}

      {/* Reports */}
      <section className="panel">
        <h2 className="text-base font-semibold mb-3">Reports</h2>
        <div className="flex flex-wrap gap-3 text-sm">
          <a className="btn btn-ghost" href={overviewReportUrl(datasetId)} target="_blank" rel="noreferrer">
            Overview PDF
          </a>
          {initialAssessment && (
            <a className="btn btn-ghost" href={assessmentReportUrl(initialAssessment.assessment_id)} target="_blank" rel="noreferrer">
              Initial assessment PDF
            </a>
          )}
          {finalAssessment && (
            <a className="btn btn-ghost" href={assessmentReportUrl(finalAssessment.assessment_id)} target="_blank" rel="noreferrer">
              Final assessment PDF
            </a>
          )}
        </div>
      </section>
    </div>
  );
}

function AssessmentView({ result }: { result: AssessmentResult }) {
  return (
    <div className="mt-5">
      <div className="flex items-center gap-4 mb-5">
        <div className="text-3xl font-bold mono">{result.overall_score ?? "N/A"}</div>
        <div className="text-xs" style={{ color: "var(--muted)" }}>
          / 100 · {result.coverage.critical} critical · {result.coverage.warnings} warnings ·{" "}
          {result.coverage.passed} passed
        </div>
      </div>

      <div className="flex flex-col gap-3 mb-5">
        {result.dimensions
          .filter((d) => d.applicable)
          .map((d) => (
            <div key={d.name} className="grid grid-cols-[160px_1fr_40px] items-center gap-3 text-sm">
              <span className="capitalize">{d.name.replace(/_/g, " ")}</span>
              <div className="track">
                <span style={{ width: `${(d.quality ?? 0) * 100}%` }} />
              </div>
              <span className="mono text-xs text-right" style={{ color: "var(--muted)" }}>
                {d.quality !== null ? Math.round(d.quality * 100) : "—"}
              </span>
            </div>
          ))}
      </div>

      <div className="flex flex-col gap-2">
        {result.dimensions
          .flatMap((d) => d.checks)
          .map((c) => (
            <div key={c.id} className="text-sm p-2 rounded flex items-start gap-2" style={{ background: "var(--surface-2)" }}>
              <span className={statusBadgeClass(c.status)}>{c.status}</span>
              <div>
                <div>{c.title}</div>
                <div className="text-xs" style={{ color: "var(--muted)" }}>
                  {c.description}
                </div>
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}
