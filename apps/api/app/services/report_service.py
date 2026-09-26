from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

from app.core.config import settings


def _new_pdf(title: str) -> FPDF:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "NUMPA", ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, title, ln=True)
    pdf.ln(4)
    pdf.set_draw_color(80, 80, 80)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)
    return pdf


def generate_overview_report(dataset_filename: str, overview: dict, out_path: Path) -> Path:
    pdf = _new_pdf(f"Dataset Overview - {dataset_filename}")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Rows: {overview['n_rows']}    Columns: {overview['n_columns']}", ln=True)
    pdf.cell(0, 7, f"Duplicate rows: {overview['duplicate_rows']}", ln=True)
    pdf.cell(0, 7, f"Overall missingness: {overview['missing_ratio'] * 100:.1f}%", ln=True)
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Columns with missing values:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    if overview["missing_by_column"]:
        for col, n in overview["missing_by_column"].items():
            pdf.cell(0, 6, f"  - {col}: {n} missing", ln=True)
    else:
        pdf.cell(0, 6, "  None", ln=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))
    return out_path


def generate_assessment_report(dataset_filename: str, assessment: dict, out_path: Path) -> Path:
    pdf = _new_pdf(f"ML Readiness Assessment ({assessment['stage']}) - {dataset_filename}")
    pdf.set_font("Helvetica", "", 12)
    score = assessment.get("overall_score")
    pdf.cell(0, 8, f"Task: {assessment['task']}    Target: {assessment.get('target') or '(none)'}", ln=True)
    pdf.cell(0, 8, f"Overall readiness score: {score if score is not None else 'N/A'}", ln=True)
    pdf.ln(4)

    for dim in assessment["dimensions"]:
        pdf.set_font("Helvetica", "B", 11)
        quality_pct = f"{dim['quality'] * 100:.0f}" if dim["quality"] is not None else "N/A"
        pdf.cell(0, 7, f"{dim['name'].replace('_', ' ').title()} - {quality_pct}", ln=True)
        pdf.set_font("Helvetica", "", 9)
        for check in dim["checks"]:
            pdf.multi_cell(0, 5, f"  [{check['status'].upper()}] {check['title']}")
        pdf.ln(2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))
    return out_path
