from app.codegen.schemas import CodeBundle
from app.codegen.writer import list_project_files, write_code_bundle
from app.llm.factory import get_groq_code
from app.llm.structured import invoke_structured
from app.models.project import Milestone, Project
from app.rag.retriever import retrieve_context
from app.tools.project_tools import set_project_context


# 1- system prompt
# 2- human prompt (context)
# 3- query (input)
def run_frontend_engineer(project: Project, milestone: Milestone) -> str:
    set_project_context(project.id)
    llm = get_groq_code()

    # small part(3000 chars) of srs for context
    srs_excerpt = project.srs_markdown[:3000] if project.srs_markdown else ""
    
    # retrieval
    rag_context = retrieve_context(
        project.id,
        f"milestone {milestone.number} frontend {milestone.title}",
    )

    existing = list_project_files(project.id)

    bundle: CodeBundle = invoke_structured(
        llm,
        CodeBundle,
        "Generate React TypeScript scaffold files for this milestone. Include 2-4 files max.",
        """Milestone: {milestone_title}
Frontend scope: {frontend_scope}
SRS excerpt: {srs_excerpt}
Context: {rag_context}
Existing files: {existing_files}
Revision feedback: {revision_feedback}

Return files with paths like frontend/src/pages/Login.tsx""",
        {
            "milestone_title": milestone.title,
            "frontend_scope": ", ".join(milestone.frontend_scope),
            "srs_excerpt": srs_excerpt,
            "rag_context": rag_context,
            "existing_files": ", ".join(existing) or "none",
            "revision_feedback": milestone.revision_feedback or "none",
        },
    )

    write_code_bundle(project.id, bundle)
    return bundle.summary or f"Frontend: wrote {len(bundle.files)} files for {milestone.title}"
