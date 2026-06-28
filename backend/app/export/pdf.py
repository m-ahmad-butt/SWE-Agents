import re
from fpdf import FPDF
from app.config import EXPORTS_DIR
from app.models.project import MilestoneStatus, Project

# file to save the text in pdf format
def _safe_text(text: str) -> str:
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _strip_inline_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text.strip()


def _write_paragraph(pdf: FPDF, text: str, height: float = 6) -> None:
    cleaned = _safe_text(_strip_inline_markdown(text))
    if not cleaned:
        pdf.ln(height / 2)
        return
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(pdf.epw, height, cleaned)


def _render_markdown(pdf: FPDF, markdown: str) -> None:
    """Render markdown text with headers, bullets, and full-width paragraphs."""
    for raw_line in markdown.replace("\r\n", "\n").split("\n"):
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            pdf.ln(3)
            continue

        if stripped.startswith("# "):
            pdf.ln(4)
            pdf.set_font("Helvetica", style="B", size=16)
            _write_paragraph(pdf, stripped[2:], 8)
            pdf.set_font("Helvetica", size=11)
            continue

        if stripped.startswith("## "):
            pdf.ln(3)
            pdf.set_font("Helvetica", style="B", size=13)
            _write_paragraph(pdf, stripped[3:], 7)
            pdf.set_font("Helvetica", size=11)
            continue

        if stripped.startswith("### "):
            pdf.ln(2)
            pdf.set_font("Helvetica", style="B", size=12)
            _write_paragraph(pdf, stripped[4:], 6)
            pdf.set_font("Helvetica", size=11)
            continue

        bullet_match = re.match(r"^[-*]\s+(.*)", stripped)
        if bullet_match:
            pdf.set_font("Helvetica", size=11)
            pdf.set_x(pdf.l_margin + 6)
            pdf.multi_cell(pdf.epw - 6, 6, f"- {_safe_text(_strip_inline_markdown(bullet_match.group(1)))}")
            continue

        num_match = re.match(r"^(\d+)\.\s+(.*)", stripped)
        if num_match:
            pdf.set_font("Helvetica", size=11)
            pdf.set_x(pdf.l_margin + 6)
            pdf.multi_cell(
                pdf.epw - 6,
                6,
                f"{num_match.group(1)}. {_safe_text(_strip_inline_markdown(num_match.group(2)))}",
            )
            continue

        pdf.set_font("Helvetica", size=11)
        _write_paragraph(pdf, stripped, 6)


def save_srs_markdown(project: Project) -> str:
    lines = ["# Software Requirements Specification", ""]
    if project.srs_markdown:
        lines.append(project.srs_markdown)
    else:
        lines.append("_SRS not generated yet._")
    lines.extend(["", "# Milestone Documentation", ""])
    for ms in project.milestones:
        badge = ""
        if ms.status == MilestoneStatus.APPROVED:
            badge = " [APPROVED]"
        elif ms.status == MilestoneStatus.PENDING_REVIEW:
            badge = " [PENDING REVIEW]"
        lines.append(f"## Milestone {ms.number}: {ms.title}{badge}")
        lines.append("")
        if ms.documentation:
            lines.append(ms.documentation)
        lines.append("")
    text = "\n".join(lines)
    path = EXPORTS_DIR / f"{project.id}_srs.md"
    path.write_text(text, encoding="utf-8")
    return str(path)


def export_srs_pdf(project: Project) -> str:
    save_srs_markdown(project)
    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    body = project.srs_markdown or "SRS not yet generated."
    _render_markdown(pdf, body)

    pdf.ln(6)
    pdf.set_font("Helvetica", style="B", size=14)
    _write_paragraph(pdf, "Milestone Documentation", 8)
    pdf.set_font("Helvetica", size=11)

    for ms in project.milestones:
        badge = ""
        if ms.status == MilestoneStatus.APPROVED:
            badge = " [APPROVED]"
        elif ms.status == MilestoneStatus.PENDING_REVIEW:
            badge = " [PENDING REVIEW]"
        pdf.ln(4)
        _render_markdown(pdf, f"## Milestone {ms.number}: {ms.title}{badge}")
        if ms.documentation:
            _render_markdown(pdf, ms.documentation)

    out_path = EXPORTS_DIR / f"{project.id}_srs.pdf"
    pdf.output(str(out_path))
    return str(out_path)


def safe_export_srs_pdf(project: Project) -> str | None:
    """Export PDF without raising — returns path or None."""
    try:
        return export_srs_pdf(project)
    except Exception:
        save_srs_markdown(project)
        return None
