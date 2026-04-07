"""Consolidation: merge duplicates, expire stale entries, trim to budget."""

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def consolidate_tier(
    tier: str,
    base_dir: str,
    stale_days: int = 90,
    max_entries: int = 50,
    skills_dir: str | None = None,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "tier": tier,
        "merged": 0,
        "expired": 0,
        "remaining": 0,
        "actions": [],
    }

    if tier == "project":
        entries_dir = _resolve_entries_dir(base_dir)
        if not entries_dir.exists():
            return report

        entries = [e for e in entries_dir.glob("*.md") if e.name != "INDEX.md"]
        report["remaining"] = len(entries)

        merged = _merge_duplicates(entries, entries_dir)
        report["merged"] = merged
        report["actions"].append(f"Merged {merged} duplicate entries")

        expired = _expire_stale(entries_dir, stale_days)
        report["expired"] = expired
        report["actions"].append(f"Flagged {expired} stale entries")

        remaining = len([e for e in entries_dir.glob("*.md") if e.name != "INDEX.md"])
        report["remaining"] = remaining

    elif tier == "skill":
        if skills_dir:
            skill_path = Path(skills_dir)
            if skill_path.exists():
                files = list(skill_path.glob("*.md"))
                report["remaining"] = len(files)

    return report


def _resolve_entries_dir(base_dir: str) -> Path:
    local = Path(base_dir) / ".magnolia" / "entries"
    if local.is_symlink():
        target = local.resolve()
        if target.exists():
            return target
    if local.exists():
        return local
    global_base = Path.home() / ".magnolia"
    from compchem_memory.storage import project_hash, get_global_project_dir

    h = project_hash(base_dir)
    global_entries = get_global_project_dir(base_dir) / "entries"
    if global_entries.exists():
        return global_entries
    return local


def _merge_duplicates(entries: list[Path], entries_dir: Path) -> int:
    titles: dict[str, list[Path]] = {}
    for e in entries:
        text = e.read_text()
        title = _get_title(text)
        normalized = title.lower().strip()
        if normalized not in titles:
            titles[normalized] = []
        titles[normalized].append(e)

    merged = 0
    for title, paths in titles.items():
        if len(paths) > 1:
            keeper = paths[0]
            for dup in paths[1:]:
                keeper_text = keeper.read_text()
                dup_text = dup.read_text()
                combined = keeper_text + "\n\n---\n\n" + dup_text
                keeper.write_text(combined)
                dup.unlink()
                merged += 1
    return merged


def _expire_stale(entries_dir: Path, stale_days: int) -> int:
    now = datetime.now(timezone.utc)
    expired = 0
    for f in entries_dir.glob("*.md"):
        if f.name == "INDEX.md":
            continue
        text = f.read_text()
        meta = _parse_frontmatter(text)
        last_verified = meta.get("last_verified", meta.get("date", ""))
        if last_verified:
            try:
                verified_date = datetime.strptime(last_verified, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
                age = (now - verified_date).days
                if age > stale_days:
                    new_text = text.replace(
                        "---", f"---\nstale: true\nstale_age_days: {age}", 1
                    )
                    f.write_text(new_text)
                    expired += 1
            except ValueError:
                pass
    return expired


def _get_title(text: str) -> str:
    meta = _parse_frontmatter(text)
    if "title" in meta:
        return meta["title"]
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[3:end].strip()) or {}
    except yaml.YAMLError:
        return {}
