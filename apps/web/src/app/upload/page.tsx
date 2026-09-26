"use client";

import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { uploadDataset, type DatasetOverview } from "@/lib/api";

export default function UploadPage() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ dataset_id: string; filename: string; overview: DatasetOverview } | null>(
    null
  );

  async function handleFile(file: File) {
    setLoading(true);
    setError(null);
    try {
      const res = await uploadDataset(file);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-7 py-10">
      <h1 className="text-2xl font-bold mb-2">Upload a dataset</h1>
      <p className="text-sm mb-8" style={{ color: "var(--muted)" }}>
        CSV or Excel. The original file is kept untouched — every cleaning step runs on a copy.
      </p>

      {!result && (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            const file = e.dataTransfer.files?.[0];
            if (file) handleFile(file);
          }}
          onClick={() => inputRef.current?.click()}
          className="panel text-center py-16 cursor-pointer"
          style={{ borderStyle: "dashed", borderColor: dragOver ? "var(--blue)" : "var(--line)" }}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".csv,.xlsx,.xls"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFile(file);
            }}
          />
          <p className="text-sm mb-1">{loading ? "Uploading…" : "Drop a file here, or click to browse"}</p>
          <p className="text-xs" style={{ color: "var(--muted)" }}>
            .csv, .xlsx, .xls — up to 50MB
          </p>
        </div>
      )}

      {error && (
        <div className="panel mt-4" style={{ borderColor: "var(--red)" }}>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {result && (
        <div className="panel">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold">{result.filename}</h3>
              <p className="text-xs" style={{ color: "var(--muted)" }}>
                {result.overview.n_rows} rows · {result.overview.n_columns} columns
              </p>
            </div>
            <span className="badge badge-pass">Uploaded</span>
          </div>

          <div className="grid grid-cols-3 gap-3 mb-5 text-sm">
            <div className="p-3 rounded-lg" style={{ background: "var(--surface-2)" }}>
              <div style={{ color: "var(--muted)", fontSize: 12 }}>Missing cells</div>
              <div className="mono">{(result.overview.missing_ratio * 100).toFixed(1)}%</div>
            </div>
            <div className="p-3 rounded-lg" style={{ background: "var(--surface-2)" }}>
              <div style={{ color: "var(--muted)", fontSize: 12 }}>Duplicate rows</div>
              <div className="mono">{result.overview.duplicate_rows}</div>
            </div>
            <div className="p-3 rounded-lg" style={{ background: "var(--surface-2)" }}>
              <div style={{ color: "var(--muted)", fontSize: 12 }}>Columns</div>
              <div className="mono">{result.overview.n_columns}</div>
            </div>
          </div>

          <button className="btn btn-primary w-full justify-center" onClick={() => router.push(`/datasets/${result.dataset_id}`)}>
            Continue to readiness assessment →
          </button>
        </div>
      )}
    </div>
  );
}
