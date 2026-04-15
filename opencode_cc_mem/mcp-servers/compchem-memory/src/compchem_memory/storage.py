"""Storage resolution: project-local memory store at project_dir/.magnolia/."""

from pathlib import Path

GLOBAL_BASE = Path.home() / ".magnolia"
PROJECTS_DIR = GLOBAL_BASE / "projects"
SKILLS_DIR = GLOBAL_BASE / "skills"


def ensure_project_store(project_dir: str) -> Path:
    """Create and return the project-local memory directory.

    Memory is stored directly under project_dir/.magnolia/ so it travels
    with the project (git, rsync, HPC sync). A symlink from the legacy
    global hash location is maintained for backward compatibility.
    """
    resolved = Path(project_dir).resolve()
    local_dir = resolved / ".magnolia"
    local_dir.mkdir(parents=True, exist_ok=True)
    for sub in ["entries", "runs", "sessions", "staging", "session-notes", "queue"]:
        (local_dir / sub).mkdir(parents=True, exist_ok=True)
    return local_dir


def resolve_project_dir(project_dir: str | None, default: str = ".") -> str:
    pd = project_dir or default
    return str(Path(pd).resolve())
