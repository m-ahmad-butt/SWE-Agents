from pathlib import Path
from app.config import GENERATED_DIR
from app.codegen.schemas import CodeBundle, GeneratedFile

# this code are for writing and reading code files
def project_root(project_id: str) -> Path:
    return GENERATED_DIR / project_id


def safe_path(project_id: str, relative_path: str) -> Path:
    root = project_root(project_id).resolve()
    target = (root / relative_path).resolve()
    if not str(target).startswith(str(root)):
        raise ValueError(f"Invalid path: {relative_path}")
    return target


def write_code_file(project_id: str, relative_path: str, content: str) -> str:
    target = safe_path(project_id, relative_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return relative_path.replace("\\", "/")


def read_code_file(project_id: str, relative_path: str) -> str:
    target = safe_path(project_id, relative_path)
    if not target.exists():
        raise FileNotFoundError(relative_path)
    return target.read_text(encoding="utf-8")


def list_project_files(project_id: str) -> list[str]:
    root = project_root(project_id)
    if not root.exists():
        return []
    files: list[str] = []
    for path in root.rglob("*"):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            files.append(rel)
    return sorted(files)


def write_code_bundle(project_id: str, bundle: CodeBundle) -> list[str]:
    written: list[str] = []
    for f in bundle.files:
        written.append(write_code_file(project_id, f.path, f.content))
    return written
