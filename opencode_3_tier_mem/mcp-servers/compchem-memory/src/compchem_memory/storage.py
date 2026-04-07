"""Storage resolution: maps project directories to ~/.magnolia/projects/{hash}/."""

import hashlib
from pathlib import Path

GLOBAL_BASE = Path.home() / ".magnolia"
PROJECTS_DIR = GLOBAL_BASE / "projects"
SKILLS_DIR = GLOBAL_BASE / "skills"


def project_hash(project_dir: str) -> str:
    resolved = Path(project_dir).resolve()
    return hashlib.sha256(str(resolved).encode()).hexdigest()[:16]


def get_global_project_dir(project_dir: str) -> Path:
    h = project_hash(project_dir)
    return PROJECTS_DIR / h


def ensure_project_store(project_dir: str) -> Path:
    resolved = Path(project_dir).resolve()
    global_dir = get_global_project_dir(project_dir)
    global_dir.mkdir(parents=True, exist_ok=True)
    for sub in ["entries", "runs", "sessions", "staging"]:
        (global_dir / sub).mkdir(parents=True, exist_ok=True)
    local_link = resolved / ".magnolia"
    if not local_link.exists():
        try:
            local_link.symlink_to(global_dir)
        except OSError:
            pass
    return global_dir


def resolve_project_dir(project_dir: str | None, default: str = ".") -> str:
    pd = project_dir or default
    return str(Path(pd).resolve())
