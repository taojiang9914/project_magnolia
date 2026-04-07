"""compchem-memory MCP server: Three-tier memory store for computational chemistry."""

import json
import os
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from compchem_memory.tiers.session import SessionManager
from compchem_memory.tiers.project import ProjectManager
from compchem_memory.tiers.skill import SkillManager
from compchem_memory.learning.assessor import assess_run
from compchem_memory.learning.consolidator import consolidate_tier
from compchem_memory.index import MemoryIndex
from compchem_memory.storage import (
    SKILLS_DIR as _SKILLS_DIR,
    ensure_project_store,
    resolve_project_dir,
)

SKILLS_DIR = Path(os.environ.get("MAGNOLIA_SKILLS_DIR", str(_SKILLS_DIR)))
PROJECT_DIR = os.environ.get("MAGNOLIA_PROJECT_DIR", ".")
GLOBAL_BASE = Path(os.path.expanduser("~/.magnolia"))

mcp = FastMCP("compchem-memory")

session_mgr: SessionManager | None = None
project_mgr: ProjectManager | None = None
skill_mgr: SkillManager | None = None
memory_idx: MemoryIndex | None = None


def _get_session_mgr(project_dir: str) -> SessionManager:
    global session_mgr
    sessions_dir = Path(project_dir) / "sessions"
    if session_mgr is None or str(session_mgr.sessions_dir) != str(sessions_dir):
        session_mgr = SessionManager(sessions_dir)
    return session_mgr


def _get_project_mgr() -> ProjectManager:
    global project_mgr
    if project_mgr is None:
        project_mgr = ProjectManager(GLOBAL_BASE)
    return project_mgr


def _get_skill_mgr() -> SkillManager:
    global skill_mgr
    if skill_mgr is None:
        skill_mgr = SkillManager(SKILLS_DIR)
    return skill_mgr


def _get_index() -> MemoryIndex:
    global memory_idx
    if memory_idx is None:
        memory_idx = MemoryIndex(GLOBAL_BASE)
    return memory_idx


def _resolve_project_store(project_dir: str | None = None) -> str:
    pd = resolve_project_dir(project_dir, PROJECT_DIR)
    ensure_project_store(pd)
    return pd


# ── Tools ────────────────────────────────────────────────────────────────────


@mcp.tool()
def memory_get_context(
    task_description: str,
    project_dir: str | None = None,
    max_entries: int = 20,
) -> str:
    """Retrieve relevant entries from all three tiers for a given task.
    Returns matching skill files, project entries, and recent session events,
    limited to max_entries total."""
    pd = _resolve_project_store(project_dir)
    results: list[dict[str, Any]] = []

    # Skill tier: keyword match against task description
    skill_m = _get_skill_mgr()
    keywords = task_description.lower().split()
    for kw in keywords[:5]:
        skills = skill_m.search_skills(keyword=kw)
        for s in skills:
            if s not in results:
                results.append(s)

    # Project tier: keyword + tag match
    proj_m = _get_project_mgr()
    for kw in keywords[:5]:
        entries = proj_m.search_entries(pd, keyword=kw)
        for e in entries:
            if e not in results:
                e["tier"] = "project"
                results.append(e)

    # Session tier: recent events
    sess_m = _get_session_mgr(pd)
    recent = sess_m.get_recent(n=10)
    for r in recent:
        r["tier"] = "session"
        results.append(r)

    # Trim to budget
    results = results[:max_entries]

    # Build content string
    content_parts = []
    for r in results:
        tier = r.get("tier", "unknown")
        if tier == "skill":
            tool_name = r.get("tool", "unknown")
            content_parts.append(f"[SKILL:{tool_name}]")
            full = skill_m.get_skill(tool_name)
            if full:
                content_parts.append(full[:500])
        elif tier == "project":
            title = r.get("title", "")
            name = r.get("name", "")
            full = proj_m.get_entry(pd, name)
            if full:
                content_parts.append(f"[PROJECT:{title}]")
                content_parts.append(full[:500])
        elif tier == "session":
            etype = r.get("event_type", "")
            content_parts.append(f"[SESSION:{etype}]")
            content_parts.append(json.dumps(r, default=str)[:200])

    return json.dumps(
        {
            "content": "\n\n".join(content_parts),
            "entry_count": len(results),
            "sources": [r.get("tier", "unknown") for r in results],
        },
        indent=2,
    )


@mcp.tool()
def memory_record_session(
    event_type: str,
    data: dict[str, Any],
    project_dir: str | None = None,
) -> str:
    """Append a structured entry to the current session log (JSONL).
    data should contain: tool_name, args, result_summary, error (if any)."""
    pd = _resolve_project_store(project_dir)
    sess_m = _get_session_mgr(pd)
    return sess_m.record(event_type, data, pd)


@mcp.tool()
def memory_record_learning(
    title: str,
    content: str,
    tags: list[str] | None = None,
    source: str = "auto",
    entry_type: str = "note",
    tools: list[str] | None = None,
    confidence: float = 0.5,
    project_dir: str | None = None,
) -> str:
    """Propose a new project-tier entry. Writes to staging area by default;
    entries become active after confirmation via memory_confirm."""
    pd = _resolve_project_store(project_dir)
    proj_m = _get_project_mgr()
    result = proj_m.create_entry(
        pd,
        title,
        content,
        tags=tags,
        source=source,
        staging=True,
        entry_type=entry_type,
        tools=tools,
        confidence=confidence,
    )
    return json.dumps({"status": "created", "path": result})


@mcp.tool()
def memory_search(
    keyword: str = "",
    tags: list[str] | None = None,
    project_dir: str | None = None,
) -> str:
    """Keyword + tag search across all tiers. Returns matching entries with
    tier label, date, confidence."""
    pd = _resolve_project_store(project_dir)
    results = []

    skill_m = _get_skill_mgr()
    results.extend(skill_m.search_skills(keyword=keyword, tags=tags))

    proj_m = _get_project_mgr()
    entries = proj_m.search_entries(pd, keyword=keyword, tags=tags)
    results.extend(entries)

    sess_m = _get_session_mgr(pd)
    session_matches = sess_m.search(keyword)
    for sm in session_matches[:5]:
        sm["tier"] = "session"
        sm["confidence"] = 0.5
        results.append(sm)

    return json.dumps(results, indent=2)


@mcp.tool()
def memory_get_run_history(
    project_dir: str | None = None,
) -> str:
    """Return run history for the current project (list of YAML records with
    status, scores, dates)."""
    pd = _resolve_project_store(project_dir)
    proj_m = _get_project_mgr()
    return json.dumps(proj_m.get_run_history(pd), indent=2)


@mcp.tool()
def memory_record_run(
    run_id: str,
    tool: str,
    status: str,
    metrics: dict[str, Any] | None = None,
    errors_solved: list[str] | None = None,
    project_dir: str | None = None,
) -> str:
    """Append a new run record to the project's run history index."""
    pd = _resolve_project_store(project_dir)
    proj_m = _get_project_mgr()
    return proj_m.record_run(pd, run_id, tool, status, metrics, errors_solved)


@mcp.tool()
def memory_promote(
    entry_name: str,
    project_dir: str | None = None,
    skills_dir: str | None = None,
) -> str:
    """Move an entry from project tier to skill tier. Requires explicit invocation
    (human-gated)."""
    pd = _resolve_project_store(project_dir)
    sd = skills_dir or str(SKILLS_DIR)
    proj_m = _get_project_mgr()
    return proj_m.promote_to_skill(pd, entry_name, sd)


@mcp.tool()
def memory_consolidate(
    tier: str = "project",
    project_dir: str | None = None,
    stale_days: int = 90,
    max_entries: int = 50,
) -> str:
    """Merge duplicates, expire stale entries, trim to budget within one tier.
    Can be called on-demand or scheduled."""
    pd = _resolve_project_store(project_dir)
    result = consolidate_tier(
        tier,
        pd,
        stale_days=stale_days,
        max_entries=max_entries,
        skills_dir=str(SKILLS_DIR),
    )
    return json.dumps(result, indent=2)


@mcp.tool()
def memory_confirm(
    entry_name: str,
    project_dir: str | None = None,
) -> str:
    """Confirm a staging entry, moving it to the active project entries."""
    pd = _resolve_project_store(project_dir)
    proj_m = _get_project_mgr()
    return proj_m.confirm_staging(pd, entry_name)


@mcp.tool()
def post_run_assess(
    run_dir: str,
    tool: str,
    exit_code: int = 0,
    project_dir: str | None = None,
) -> str:
    """After a computation completes: check exit code, verify output files exist,
    extract metrics, flag quality issues. Records run in memory automatically."""
    assessment = assess_run(run_dir, tool, exit_code)
    pd = _resolve_project_store(project_dir)
    proj_m = _get_project_mgr()
    run_id = Path(run_dir).name
    proj_m.record_run(
        pd,
        run_id=run_id,
        tool=tool,
        status="success" if exit_code == 0 else "failed",
        metrics=assessment.get("metrics", {}),
        errors_solved=[],
    )
    sess_m = _get_session_mgr(pd)
    sess_m.record(
        "post_run_assess",
        {"run_dir": run_dir, "tool": tool, "assessment": assessment},
        pd,
    )
    return json.dumps(assessment, indent=2)


# ── Resources ────────────────────────────────────────────────────────────────


@mcp.resource("memory://skills/{tool_name}")
def get_skill_resource(tool_name: str) -> str:
    """Full skill file content for a given tool."""
    skill_m = _get_skill_mgr()
    content = skill_m.get_skill(tool_name)
    return content or f"No skill found for {tool_name}"


@mcp.resource("memory://project/index")
def get_project_index() -> str:
    """Project-tier entry catalogue for current project."""
    pd = _resolve_project_store()
    proj_m = _get_project_mgr()
    return json.dumps(proj_m.list_entries(pd), indent=2)


@mcp.resource("memory://project/entry/{name}")
def get_project_entry(name: str) -> str:
    """A single project-tier entry by name."""
    pd = _resolve_project_store()
    proj_m = _get_project_mgr()
    content = proj_m.get_entry(pd, name)
    return content or f"Entry not found: {name}"


@mcp.resource("memory://runs/index")
def get_runs_index() -> str:
    """Run history index for current project."""
    pd = _resolve_project_store()
    proj_m = _get_project_mgr()
    return json.dumps(proj_m.get_run_history(pd), indent=2)


if __name__ == "__main__":
    mcp.run()
