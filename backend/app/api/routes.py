import io
import zipfile
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from app.agents.negotiation_agent import run_negotiation_agent
from app.agents.requirement_engineer import run_requirement_engineer
from app.chains.pipeline import (
    advance_project,
    approve_milestone,
    reject_milestone,
    run_planning_phase,
    run_proposal_to_srs,
)
from app.codegen.writer import list_project_files, project_root, read_code_file
from app.export.pdf import export_srs_pdf
from app.models.project import Project, ProjectPhase
from app.storage.json_store import list_project_summaries, load_project, save_project

router = APIRouter(prefix="/api")

class CreateProjectRequest(BaseModel):
    query: str


class MessageRequest(BaseModel):
    message: str


class RejectRequest(BaseModel):
    feedback: str


@router.get("/projects")
def list_all_projects() -> dict:
    return {"projects": list_project_summaries()}


@router.post("/projects")
def create_project(body: CreateProjectRequest) -> dict:
    title = body.query[:80] + ("..." if len(body.query) > 80 else "")
    project = Project(title=title, initial_query=body.query)
    project.status_message = "Requirement Engineer is gathering requirements..."
    project.active_agent = "requirement_engineer"
    project.add_message("user", body.query)
    project.add_message(
        "assistant",
        "Hi! I'm your Requirement Engineer. Let's gather your project requirements.\n\n"
        "First question: Is this a **web**, **mobile**, or **desktop** application?",
        agent="requirement_engineer",
    )
    save_project(project)
    return project.to_public_dict()


@router.get("/projects/{project_id}")
def get_project(project_id: str) -> dict:
    try:
        project = load_project(project_id)
        if project.phase == ProjectPhase.COMPLETED and not project.run_guide_markdown:
            from app.export.run_guide import save_run_guide

            project.run_guide_markdown = save_run_guide(project)
            project.generated_files = list_project_files(project_id)
            save_project(project)
        return project.to_public_dict()
    except FileNotFoundError:
        raise HTTPException(404, "Project not found")


def _requirements_done(reply: str) -> bool:
    lower = reply.lower()
    return any(
        phrase in lower
        for phrase in (
            "planning analyst",
            "collected all requirements",
            "passing them to",
            "requirements complete",
        )
    )


def _proposal_done(reply: str) -> bool:
    lower = reply.lower()
    return any(
        phrase in lower
        for phrase in ("proposal accepted", "generate your srs", "accepted. we will")
    )


def _is_approval(message: str) -> bool:
    """Treat common affirmative replies as milestone/proposal approval."""
    m = message.lower().strip()
    if m in {
        "yes",
        "ok",
        "okay",
        "done",
        "yes done",
        "yep",
        "sure",
        "approve",
        "approved",
        "accept",
        "accepted",
        "lgtm",
        "looks good",
        "all good",
        "good to go",
    }:
        return True
    approval_phrases = (
        "approve",
        "approved",
        "accept",
        "accepted",
        "yes done",
        "looks good",
        "all good",
        "good to go",
    )
    return any(p in m for p in approval_phrases)


def _is_revision_request(message: str) -> bool:
    """Only treat as revision when the user clearly asks for changes."""
    if _is_approval(message):
        return False
    m = message.lower().strip()
    revision_phrases = (
        "change",
        "revise",
        "revision",
        "reject",
        "fix",
        "wrong",
        "update",
        "not good",
        "redo",
        "improve",
    )
    return any(p in m for p in revision_phrases)


@router.post("/projects/{project_id}/message")
def post_message(project_id: str, body: MessageRequest) -> dict:
    project = load_project(project_id)
    msg_lower = body.message.lower().strip()

    if msg_lower in ("continue", "retry", "resume"):
        try:
            project = advance_project(project_id)
            return project.to_public_dict()
        except Exception as e:
            project = load_project(project_id)
            project.add_message(
                "assistant",
                f"Could not continue: {e}. Try again or type 'approve' if reviewing a milestone.",
                agent=project.active_agent,
            )
            save_project(project)
            return project.to_public_dict()

    project.add_message("user", body.message)
    save_project(project)

    if project.phase == ProjectPhase.REQUIREMENTS:
        msg_lower = body.message.lower().strip()
        if msg_lower in ("done", "that's all", "thats all", "complete", "finish"):
            project.requirements_complete = True
            save_project(project)
            try:
                project = run_planning_phase(project_id)
            except Exception as e:
                project = load_project(project_id)
                project.add_message(
                    "assistant",
                    f"Planning step failed: {e}. Please try again.",
                    agent="planning_analyst",
                )
                save_project(project)
            return project.to_public_dict()

        reply = run_requirement_engineer(project, body.message)
        project = load_project(project_id)
        if not project.requirements_complete and _requirements_done(reply):
            project.requirements_complete = True
        project.add_message("assistant", reply, agent="requirement_engineer")
        save_project(project)
        if project.requirements_complete:
            try:
                project = run_planning_phase(project_id)
            except Exception as e:
                project = load_project(project_id)
                project.add_message(
                    "assistant",
                    f"Planning step failed: {e}. Please try again.",
                    agent="planning_analyst",
                )
                save_project(project)
        return project.to_public_dict()

    if project.phase == ProjectPhase.NEGOTIATION:
        reply = run_negotiation_agent(project, body.message)
        project = load_project(project_id)
        if not project.proposal_accepted and _proposal_done(reply):
            project.proposal_accepted = True
        project.add_message("assistant", reply, agent="negotiation_agent")
        save_project(project)
        if project.proposal_accepted:
            try:
                project = run_proposal_to_srs(project_id)
            except Exception as e:
                project = load_project(project_id)
                project.add_message(
                    "assistant",
                    f"Next step failed: {e}. Type **continue** to retry.",
                    agent="srs_generator",
                )
                save_project(project)
        return project.to_public_dict()

    if project.phase == ProjectPhase.PROPOSAL_REVIEW:
        if _is_approval(body.message):
            project.proposal_accepted = True
            save_project(project)
            try:
                project = run_proposal_to_srs(project_id)
            except Exception as e:
                project = load_project(project_id)
                project.add_message(
                    "assistant",
                    f"Next step failed: {e}. Type **continue** to retry.",
                    agent="srs_generator",
                )
                save_project(project)
        else:
            project.add_message(
                "assistant",
                "Please confirm: reply 'accept' to proceed with the proposal.",
                agent="negotiation_agent",
            )
            save_project(project)
        return project.to_public_dict()

    if project.phase == ProjectPhase.MILESTONE_REVIEW:
        ms = project.current_milestone()
        if ms and _is_approval(body.message):
            project = approve_milestone(project_id, ms.number)
        elif ms and _is_revision_request(body.message):
            project = reject_milestone(project_id, ms.number, body.message)
        elif ms:
            project.add_message(
                "assistant",
                "Please reply **approve** (or **yes done**) to accept this milestone, "
                "or describe the changes you want.",
                agent="customer_review",
            )
            save_project(project)
        return project.to_public_dict()

    project.add_message(
        "assistant",
        f"Current phase: {project.phase.value}. {project.status_message}",
        agent=project.active_agent,
    )
    save_project(project)
    return project.to_public_dict()


@router.post("/projects/{project_id}/advance")
def advance(project_id: str) -> dict:
    project = advance_project(project_id)
    return project.to_public_dict()


@router.post("/projects/{project_id}/milestones/{n}/approve")
def approve(project_id: str, n: int) -> dict:
    project = approve_milestone(project_id, n)
    return project.to_public_dict()


@router.post("/projects/{project_id}/milestones/{n}/reject")
def reject(project_id: str, n: int, body: RejectRequest) -> dict:
    project = reject_milestone(project_id, n, body.feedback)
    return project.to_public_dict()


@router.get("/projects/{project_id}/run-guide")
def get_run_guide(project_id: str) -> dict:
    try:
        project = load_project(project_id)
        if project.run_guide_markdown:
            return {"run_guide_markdown": project.run_guide_markdown}
        from app.export.run_guide import save_run_guide

        if project.phase.value == "completed":
            content = save_run_guide(project)
            project.run_guide_markdown = content
            project.generated_files = list_project_files(project_id)
            save_project(project)
            return {"run_guide_markdown": content}
        return {"run_guide_markdown": ""}
    except FileNotFoundError:
        raise HTTPException(404, "Project not found")


@router.get("/projects/{project_id}/run-guide/download")
def download_run_guide(project_id: str):
    try:
        project = load_project(project_id)
        content = project.run_guide_markdown
        if not content:
            from app.export.run_guide import generate_run_guide

            content = generate_run_guide(project)
        from fastapi.responses import Response

        return Response(
            content=content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=README_{project_id}.md"},
        )
    except FileNotFoundError:
        raise HTTPException(404, "Project not found")


@router.get("/projects/{project_id}/srs/pdf")
def download_pdf(project_id: str):
    try:
        project = load_project(project_id)
        path = export_srs_pdf(project)
        return FileResponse(
            path,
            filename=f"project_{project_id}_srs.pdf",
            media_type="application/pdf",
        )
    except FileNotFoundError:
        raise HTTPException(404, "Project not found")
    except Exception as e:
        raise HTTPException(500, f"PDF export failed: {e}")


@router.get("/projects/{project_id}/srs/markdown")
def get_srs_markdown(project_id: str):
    try:
        project = load_project(project_id)
        from app.export.pdf import save_srs_markdown

        save_srs_markdown(project)
        return {
            "srs_markdown": project.srs_markdown or "",
            "milestones": [
                {
                    "number": m.number,
                    "title": m.title,
                    "status": m.status.value,
                    "documentation": m.documentation,
                }
                for m in project.milestones
            ],
        }
    except FileNotFoundError:
        raise HTTPException(404, "Project not found")


@router.get("/projects/{project_id}/code")
def list_code(project_id: str) -> dict:
    return {"files": list_project_files(project_id)}


@router.get("/projects/{project_id}/code/{path:path}")
def read_code(project_id: str, path: str) -> dict:
    try:
        content = read_code_file(project_id, path)
        return {"path": path, "content": content}
    except FileNotFoundError:
        raise HTTPException(404, "File not found")
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/projects/{project_id}/code/download")
def download_code(project_id: str):
    root = project_root(project_id)
    if not root.exists():
        raise HTTPException(404, "No generated code")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in root.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(root).as_posix()
                zf.write(file_path, arcname)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=project_{project_id}.zip"},
    )
