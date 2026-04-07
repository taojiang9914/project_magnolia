"""Session tier: append-only JSONL log for the current conversation."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SessionManager:
    def __init__(self, sessions_dir: Path):
        self.sessions_dir = sessions_dir
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self._current_session: Path | None = None

    def _get_session_path(self) -> Path:
        if self._current_session and self._current_session.exists():
            return self._current_session
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
        fname = f"{ts}.jsonl"
        self._current_session = self.sessions_dir / fname
        return self._current_session

    def record(
        self,
        event_type: str,
        data: dict[str, Any],
        project_dir: str | None = None,
    ) -> str:
        path = self._get_session_path()
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            **data,
        }
        with open(path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return str(path)

    def get_recent(
        self, n: int = 50, project_dir: str | None = None
    ) -> list[dict[str, Any]]:
        path = self._get_session_path()
        if not path.exists():
            return []
        with open(path) as f:
            lines = f.readlines()
        return [json.loads(line) for line in lines[-n:]]

    def search(
        self, keyword: str, project_dir: str | None = None
    ) -> list[dict[str, Any]]:
        path = self._get_session_path()
        if not path.exists():
            return []
        results = []
        with open(path) as f:
            for line in f:
                entry = json.loads(line)
                if keyword.lower() in json.dumps(entry).lower():
                    results.append(entry)
        return results

    def start_new_session(self) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
        self._current_session = self.sessions_dir / f"{ts}.jsonl"
        return str(self._current_session)

    def get_session_log_path(self) -> str | None:
        if self._current_session and self._current_session.exists():
            return str(self._current_session)
        return None

    def count_events_since(self, cursor: str) -> tuple[int, int]:
        path = self._get_session_path()
        if not path.exists():
            return 0, 0
        events = []
        cursor_idx = 0
        with open(path) as f:
            for line in f:
                try:
                    ev = json.loads(line.strip())
                    events.append(ev)
                except json.JSONDecodeError:
                    continue
        if cursor:
            for i, ev in enumerate(events):
                if ev.get("timestamp", "") == cursor:
                    cursor_idx = i + 1
                    break
        since = events[cursor_idx:]
        text = json.dumps(since)
        tokens = len(text) // 4
        tool_calls = sum(
            1
            for ev in since
            if ev.get("event_type") in ("tool_call", "tool_success", "tool_error")
        )
        return tokens, tool_calls
