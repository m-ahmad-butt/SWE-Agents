from app.codegen.schemas import CodeBundle
from app.codegen.writer import list_project_files, write_code_bundle
from app.llm.factory import get_groq_code
from app.llm.structured import invoke_structured
from app.models.project import Milestone, Project
from app.rag.retriever import retrieve_context
from app.tools.project_tools import set_project_context


def run_backend_engineer(project: Project, milestone: Milestone) -> str:
    set_project_context(project.id)
    llm = get_groq_code()
    srs_excerpt = project.srs_markdown[:3000] if project.srs_markdown else ""
    rag_context = retrieve_context(
        project.id,
        f"milestone {milestone.number} backend {milestone.title}",
    )
    existing = list_project_files(project.id)

    bundle: CodeBundle = invoke_structured(
        llm,
        CodeBundle,
        "Generate FastAPI Python scaffold files for this milestone. Include 2-4 files max.",
        """Milestone: {milestone_title}
Backend scope: {backend_scope}
SRS excerpt: {srs_excerpt}
Context: {rag_context}
Existing files: {existing_files}
Revision feedback: {revision_feedback}

Return files with paths like backend/main.py, backend/routes/auth.py""",
        {
            "milestone_title": milestone.title,
            "backend_scope": ", ".join(milestone.backend_scope),
            "srs_excerpt": srs_excerpt,
            "rag_context": rag_context,
            "existing_files": ", ".join(existing) or "none",
            "revision_feedback": milestone.revision_feedback or "none",
        },
    )

    write_code_bundle(project.id, bundle)
    return bundle.summary or f"Backend: wrote {len(bundle.files)} files for {milestone.title}"
