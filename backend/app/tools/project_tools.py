from langchain_core.tools import tool
from app.codegen.schemas import CodeBundle
from app.codegen.writer import (
    list_project_files,
    read_code_file,
    write_code_bundle,
    write_code_file,
)
from app.models.project import Project
from app.storage.json_store import load_project, save_project

# Module-level project context set before agent runs
_current_project_id: str | None = None


def set_project_context(project_id: str) -> None:
    global _current_project_id
    _current_project_id = project_id


def get_project_context() -> str:
    if not _current_project_id:
        raise RuntimeError("No project context set")
    return _current_project_id


@tool
def mark_requirements_complete(summary: str) -> str:
    """Call when requirements gathering is complete. Pass a structured summary of all requirements."""
    pid = get_project_context()
    project = load_project(pid)
    project.requirements_complete = True
    project.status_message = "Requirements collected. Planning Analyst is working..."
    save_project(project)
    return "Requirements marked complete."


@tool
def accept_proposal(notes: str) -> str:
    """Call when the customer accepts the negotiated proposal."""
    pid = get_project_context()
    project = load_project(pid)
    project.proposal_accepted = True
    project.status_message = "Proposal accepted. Generating SRS..."
    save_project(project)
    return "Proposal accepted."


@tool
def write_code_file_tool(path: str, content: str) -> str:
    """Write a generated code file. Path must be relative e.g. backend/routes/auth.py"""
    pid = get_project_context()
    rel = write_code_file(pid, path, content)
    project = load_project(pid)
    if rel not in project.generated_files:
        project.generated_files.append(rel)
    project.status_message = f"Writing {rel}..."
    save_project(project)
    return f"Wrote {rel}"


@tool
def read_code_file_tool(path: str) -> str:
    """Read an existing generated code file."""
    pid = get_project_context()
    return read_code_file(pid, path)


@tool
def list_project_files_tool() -> str:
    """List all generated files for this project."""
    pid = get_project_context()
    files = list_project_files(pid)
    return "\n".join(files) if files else "No files yet."


# toolkit -> list of tools
def get_requirement_tools():
    return [mark_requirements_complete]


def get_negotiation_tools():
    return [accept_proposal]


def get_code_tools():
    return [write_code_file_tool, read_code_file_tool, list_project_files_tool]
