"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { listDatasets, type DatasetSummary } from "@/lib/api";

export default function DashboardPage() {
  const [datasets, setDatasets] = useState<DatasetSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listDatasets()
      .then(setDatasets)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-7 py-10">
      <div className="flex items-center justify-between flex-wrap gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-sm mt-1" style={{ color: "var(--muted)" }}>
            Every dataset moves through upload, readiness, cleaning, and comparison.
          </p>
        </div>
        <Link href="/upload" className="btn btn-primary">
          Upload dataset
        </Link>
      </div>

      {error && (
        <div className="panel mb-6" style={{ borderColor: "var(--red)" }}>
          <p className="text-sm">
            Could not reach the NUMPA API ({error}). Make sure the backend is running at{" "}
            <span className="mono">NEXT_PUBLIC_API_URL</span> (default <span className="mono">http://localhost:8000</span>).
          </p>
        </div>
      )}

      {!error && datasets === null && (
        <p className="text-sm" style={{ color: "var(--muted)" }}>
          Loading datasets…
        </p>
      )}

      {datasets && datasets.length === 0 && (
        <div className="panel text-center py-14">
          <p className="text-sm mb-4" style={{ color: "var(--muted)" }}>
            No datasets yet. Upload a CSV or Excel file to run your first readiness assessment.
          </p>
          <Link href="/upload" className="btn btn-primary">
            Upload your first dataset
          </Link>
        </div>
      )}

      {datasets && datasets.length > 0 && (
        <div className="panel p-0 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left" style={{ color: "var(--muted)" }}>
                <th className="px-5 py-3 font-normal text-xs uppercase tracking-wide">Dataset</th>
                <th className="px-5 py-3 font-normal text-xs uppercase tracking-wide">Rows</th>
                <th className="px-5 py-3 font-normal text-xs uppercase tracking-wide">Columns</th>
                <th className="px-5 py-3 font-normal text-xs uppercase tracking-wide">Uploaded</th>
                <th className="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((d) => (
                <tr key={d.dataset_id} style={{ borderTop: "1px solid var(--line)" }}>
                  <td className="px-5 py-3 font-medium">{d.filename}</td>
                  <td className="px-5 py-3 mono" style={{ color: "var(--muted)" }}>
                    {d.n_rows}
                  </td>
                  <td className="px-5 py-3 mono" style={{ color: "var(--muted)" }}>
                    {d.n_cols}
                  </td>
                  <td className="px-5 py-3 mono" style={{ color: "var(--muted)" }}>
                    {new Date(d.uploaded_at).toLocaleString()}
                  </td>
                  <td className="px-5 py-3 text-right">
                    <Link href={`/datasets/${d.dataset_id}`} style={{ color: "var(--blue)" }}>
                      Open →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
