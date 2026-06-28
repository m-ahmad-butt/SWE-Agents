import json
from pathlib import Path
from app.config import PROJECTS_DIR
from app.models.project import Project


def _path(project_id: str) -> Path:
    return PROJECTS_DIR / f"{project_id}.json"


def save_project(project: Project) -> Project:
    project.touch()
    _path(project.id).write_text(
        project.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return project


def load_project(project_id: str) -> Project:
    path = _path(project_id)
    if not path.exists():
        raise FileNotFoundError(f"Project {project_id} not found")
    data = json.loads(path.read_text(encoding="utf-8"))
    return Project.model_validate(data)


def list_projects() -> list[str]:
    return [p.stem for p in PROJECTS_DIR.glob("*.json")]


def list_project_summaries() -> list[dict]:
    summaries: list[dict] = []
    for path in PROJECTS_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            summaries.append({
                "id": data.get("id", path.stem),
                "title": data.get("title", "Untitled"),
                "phase": data.get("phase", "requirements"),
                "active_agent": data.get("active_agent", ""),
                "status_message": data.get("status_message", ""),
                "updated_at": data.get("updated_at", ""),
                "created_at": data.get("created_at", ""),
            })
        except (json.JSONDecodeError, OSError):
            continue
    summaries.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return summaries
