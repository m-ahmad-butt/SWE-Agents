from app.codegen.writer import list_project_files
from app.llm.factory import get_groq_doc
from app.llm.structured import invoke_structured
from app.models.milestone_doc import MilestoneDocumentation
from app.models.project import Milestone, Project
from app.rag.retriever import retrieve_context
from app.rag.store import index_text


def run_documentation_agent(
    project: Project,
    milestone: Milestone,
    backend_summary: str,
    frontend_summary: str,
) -> MilestoneDocumentation:
    llm = get_groq_doc()
    files = list_project_files(project.id)
    rag_context = retrieve_context(
        project.id,
        f"milestone {milestone.number} documentation {milestone.title}",
    )

    doc: MilestoneDocumentation = invoke_structured(
        llm,
        MilestoneDocumentation,
        "Write milestone documentation: completed features, pending items, summary.",
        """Milestone: {milestone_title}
Generated files: {generated_files}
Context: {rag_context}
Backend: {backend_summary}
Frontend: {frontend_summary}""",
        {
            "milestone_title": milestone.title,
            "generated_files": ", ".join(files),
            "rag_context": rag_context,
            "backend_summary": backend_summary,
            "frontend_summary": frontend_summary,
        },
    )

    milestone.documentation = (
        f"# Milestone {milestone.number}: {doc.title}\n\n"
        f"{doc.summary}\n\n"
        "## Completed\n"
        + "\n".join(f"- {f}" for f in doc.completed_features)
        + "\n\n## Pending\n"
        + "\n".join(f"- {f}" for f in doc.pending_features)
    )

    index_text(
        project.id,
        milestone.documentation,
        metadata={"milestone": milestone.number, "type": "milestone_doc"},
    )
    if project.srs_markdown:
        index_text(
            project.id,
            project.srs_markdown,
            metadata={"type": "srs"},
        )

    return doc
