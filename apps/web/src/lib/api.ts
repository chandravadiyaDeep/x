const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(options?.body && !(options.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...options?.headers,
    },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // response wasn't JSON — keep statusText
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

// ---------- Types ----------

export interface DatasetOverview {
  n_rows: number;
  n_columns: number;
  columns: string[];
  dtypes: Record<string, string>;
  missing_by_column: Record<string, number>;
  missing_ratio: number;
  duplicate_rows: number;
  preview: Record<string, unknown>[];
  numeric_summary: Record<string, { mean: number; std: number; min: number; max: number }>;
}

export interface DatasetSummary {
  dataset_id: string;
  filename: string;
  n_rows: number;
  n_cols: number;
  uploaded_at: string;
}

export interface CheckResult {
  id: string;
  title: string;
  description: string;
  status: "pass" | "warning" | "critical";
  category: "confirmed" | "suspected" | "unknown" | "not_applicable";
  measurement: Record<string, unknown>;
}

export interface DimensionResult {
  name: string;
  quality: number | null;
  weight: number;
  applicable: boolean;
  checks: CheckResult[];
}

export interface AssessmentResult {
  assessment_id: string;
  task: string;
  target: string | null;
  overall_score: number | null;
  coverage: {
    total_checks: number;
    critical: number;
    warnings: number;
    passed: number;
    not_applicable_dimensions: string[];
  };
  dimensions: DimensionResult[];
  generated_at: string;
}

export interface PipelineStepDef {
  id: string;
  type: string;
  params: Record<string, unknown>;
}

export interface StepExecutionRecord {
  step_id: string;
  type: string;
  summary: string;
  warnings: string[];
  rows_before: number;
  rows_after: number;
}

export interface PipelineRunResult {
  execution_id: string;
  original_rows: number;
  final_rows: number;
  steps: StepExecutionRecord[];
  cleaned_preview: Record<string, unknown>[];
}

// ---------- API calls ----------

export async function uploadDataset(file: File): Promise<{ dataset_id: string; filename: string; overview: DatasetOverview }> {
  const form = new FormData();
  form.append("file", file);
  return request(`/v1/datasets`, { method: "POST", body: form });
}

export async function listDatasets(): Promise<DatasetSummary[]> {
  return request(`/v1/datasets`);
}

export async function getDataset(id: string): Promise<{ dataset_id: string; filename: string; overview: DatasetOverview }> {
  return request(`/v1/datasets/${id}`);
}

export async function runAssessment(params: {
  dataset_id: string;
  task: string;
  target?: string | null;
  stage?: "initial" | "final";
}): Promise<AssessmentResult> {
  return request(`/v1/readiness/assess`, { method: "POST", body: JSON.stringify(params) });
}

export async function listOperations(): Promise<{ operations: string[] }> {
  return request(`/v1/cleaning/operations`);
}

export async function runCleaningPipeline(params: {
  dataset_id: string;
  name?: string;
  steps: PipelineStepDef[];
}): Promise<PipelineRunResult> {
  return request(`/v1/cleaning/run`, { method: "POST", body: JSON.stringify(params) });
}

export function overviewReportUrl(datasetId: string): string {
  return `${API_BASE}/v1/reports/overview/${datasetId}`;
}

export function assessmentReportUrl(assessmentId: string): string {
  return `${API_BASE}/v1/reports/assessment/${assessmentId}`;
}
