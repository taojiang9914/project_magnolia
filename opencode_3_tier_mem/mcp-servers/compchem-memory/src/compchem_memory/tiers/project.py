"""Project tier: durable, human-readable notes scoped to a project directory."""

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ENTRY_TYPES = (
    "success_pattern",
    "error_resolution",
    "parameter_guidance",
    "workflow_note",
    "note",
)


class ProjectManager:
    def __init__(self, global_base: Path):
        self.global_base = global_base

    def _project_store(self, project_dir: str) -> Path:
        local = Path(project_dir) / ".magnolia"
        if local.is_symlink():
            target = local.resolve()
            if target.exists():
                return target
        return local

    def _entries_dir(self, project_dir: str) -> Path:
        d = self._project_store(project_dir) / "entries"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _runs_dir(self, project_dir: str) -> Path:
        d = self._project_store(project_dir) / "runs"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _staging_dir(self, project_dir: str) -> Path:
        d = self._project_store(project_dir) / "staging"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _index_path(self, project_dir: str) -> Path:
        return self._entries_dir(project_dir) / "INDEX.md"

    def _runs_index_path(self, project_dir: str) -> Path:
        return self._runs_dir(project_dir) / "INDEX.yaml"

    def create_entry(
        self,
        project_dir: str,
        title: str,
        content: str,
        tags: list[str] | None = None,
        source: str = "auto",
        staging: bool = False,
        entry_type: str = "note",
        tools: list[str] | None = None,
        confidence: float = 0.5,
        related_entries: list[str] | None = None,
    ) -> str:
        if entry_type not in ENTRY_TYPES:
            entry_type = "note"
        if staging:
            base = self._staging_dir(project_dir)
        else:
            base = self._entries_dir(project_dir)
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", title)[:60].strip("_")
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        fname = f"{ts}_{slug}.md"
        fpath = base / fname
        now_iso = datetime.now(timezone.utc).isoformat()
        now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        frontmatter = {
            "id": ts,
            "type": entry_type,
            "title": title,
            "description": content[:200],
            "tools": tools or [],
            "tags": tags or [],
            "created": now_iso,
            "updated": now_iso,
            "date": now_date,
            "last_verified": now_date,
            "author": source,
            "source": source,
            "observation_count": 1,
            "confidence": confidence,
        }
        if related_entries:
            frontmatter["related_entries"] = related_entries
        fm_str = "---\n" + yaml.dump(frontmatter, default_flow_style=False) + "---\n"
        fpath.write_text(fm_str + "\n" + content + "\n")
        if not staging:
            self._update_index(project_dir)
        return str(fpath)

    def get_entry(self, project_dir: str, name: str) -> str | None:
        entries_dir = self._entries_dir(project_dir)
        normalized = re.sub(r"[^a-zA-Z0-9]+", "_", name).lower()
        for f in entries_dir.glob("*.md"):
            fn_norm = re.sub(r"[^a-zA-Z0-9]+", "_", f.stem).lower()
            if f.name == name or f.stem == name or normalized in fn_norm:
                return f.read_text()
        return None

    def list_entries(self, project_dir: str) -> list[dict[str, Any]]:
        entries_dir = self._entries_dir(project_dir)
        results: list[dict[str, Any]] = []
        md_files = sorted(entries_dir.glob("*.md"))
        for f in md_files:
            if f.name == "INDEX.md":
                continue
            text = f.read_text()
            meta = self._parse_frontmatter(text)
            results.append(
                {
                    "name": f.name,
                    "title": meta.get("title", f.stem),
                    "type": meta.get("type", "note"),
                    "date": meta.get("date", ""),
                    "tags": meta.get("tags", []),
                    "tools": meta.get("tools", []),
                    "confidence": meta.get("confidence", 0.5),
                    "observation_count": meta.get("observation_count", 0),
                    "source": meta.get("source", ""),
                    "path": str(f),
                }
            )
        return results

    def search_entries(
        self, project_dir: str, keyword: str = "", tags: list[str] | None = None
    ) -> list[dict[str, Any]]:
        entries = self.list_entries(project_dir)
        results: list[dict[str, Any]] = []
        for entry in entries:
            text_content = self.get_entry(project_dir, entry["name"]) or ""
            match = True
            if keyword:
                match = keyword.lower() in (text_content + str(entry)).lower()
            if match and tags:
                entry_tags_lower = [t.lower() for t in entry.get("tags", [])]
                if not any(t.lower() in entry_tags_lower for t in tags):
                    match = False
            if match:
                entry["tier"] = "project"
                results.append(entry)
        return results

    def promote_to_skill(
        self, project_dir: str, entry_name: str, skills_dir: str
    ) -> str:
        entries_dir = self._entries_dir(project_dir)
        source = None
        for f in entries_dir.glob("*.md"):
            if f.name == entry_name or entry_name in f.name:
                source = f
                break
        if not source:
            raise FileNotFoundError(f"Entry not found: {entry_name}")
        skills_path = Path(skills_dir)
        skills_path.mkdir(parents=True, exist_ok=True)
        dest = skills_path / source.name
        dest.write_text(source.read_text())
        source.unlink()
        self._update_index(project_dir)
        return str(dest)

    def confirm_staging(self, project_dir: str, entry_name: str) -> str:
        staging = self._staging_dir(project_dir)
        entries = self._entries_dir(project_dir)
        source = None
        for f in staging.glob("*.md"):
            if f.name == entry_name or entry_name in f.name or entry_name in f.stem:
                source = f
                break
        if not source:
            raise FileNotFoundError(f"Staging entry not found: {entry_name}")
        dest = entries / source.name
        dest.write_text(source.read_text())
        source.unlink()
        self._update_index(project_dir)
        return str(dest)

    def record_run(
        self,
        project_dir: str,
        run_id: str,
        tool: str,
        status: str,
        metrics: dict[str, Any] | None = None,
        errors_solved: list[str] | None = None,
    ) -> str:
        runs_dir = self._runs_dir(project_dir)
        record = {
            "run_id": run_id,
            "tool": tool,
            "status": status,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "metrics": metrics or {},
            "errors_solved": errors_solved or [],
        }
        ts = datetime.now(timezone.utc).strftime("%Y%m%d")
        fname = f"{ts}_{run_id}.yaml"
        fpath = runs_dir / fname
        fpath.write_text(yaml.dump(record, default_flow_style=False))
        self._update_runs_index(project_dir)
        return str(fpath)

    def get_run_history(self, project_dir: str) -> list[dict[str, Any]]:
        runs_dir = self._runs_dir(project_dir)
        results: list[dict[str, Any]] = []
        for f in sorted(runs_dir.glob("*.yaml")):
            if f.name == "INDEX.yaml":
                continue
            record = yaml.safe_load(f.read_text())
            record["path"] = str(f)
            results.append(record)
        return results

    def _parse_frontmatter(self, text: str) -> dict[str, Any]:
        if not text.startswith("---"):
            return {}
        end = text.find("---", 3)
        if end == -1:
            return {}
        fm = text[3:end].strip()
        try:
            return yaml.safe_load(fm) or {}
        except yaml.YAMLError:
            return {}

    def _update_index(self, project_dir: str) -> None:
        entries = self.list_entries(project_dir)
        index_path = self._index_path(project_dir)
        lines = ["# Project-Tier Entry Index\n\n"]
        lines.append(
            f"**Last updated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n"
        )
        if not entries:
            lines.append("_No entries yet._\n")
        else:
            for e in entries:
                tags = ", ".join(e.get("tags", []))
                entry_type = e.get("type", "note")
                lines.append(
                    f"- **{e['title']}** (`{e['name']}`) [{entry_type}] — {e['date']} [{tags}]\n"
                )
        index_path.write_text("".join(lines))

    def _update_runs_index(self, project_dir: str) -> None:
        runs = self.get_run_history(project_dir)
        runs_dir = self._runs_dir(project_dir)

        # Backward compat: remove old INDEX.md if it exists
        old_index = runs_dir / "INDEX.md"
        if old_index.exists():
            old_index.unlink()

        index_path = self._runs_index_path(project_dir)
        index_data = {
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "runs": [
                {
                    "run_id": r.get("run_id", ""),
                    "tool": r.get("tool", ""),
                    "status": r.get("status", ""),
                    "date": r.get("date", ""),
                }
                for r in runs
            ],
        }
        index_path.write_text(yaml.dump(index_data, default_flow_style=False))
