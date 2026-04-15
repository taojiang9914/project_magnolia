"""CLI for non-MCP memory operations (HPC-compatible, no server required)."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from compchem_memory.storage import ensure_project_store


def cmd_log_bash(args: argparse.Namespace) -> int:
    """Log a bash command execution to the project's session JSONL."""
    project_dir = args.project_dir or "."
    local_dir = ensure_project_store(project_dir)
    sessions_dir = local_dir / "sessions"

    ts = datetime.now(timezone.utc).isoformat()
    fname = f"{ts.replace(':', '').replace('+', '')}.jsonl"
    # Use a rolling filename based on date
    fname = datetime.now(timezone.utc).strftime("%Y-%m-%d.jsonl")
    path = sessions_dir / fname

    entry = {
        "timestamp": ts,
        "event_type": "bash_execution",
        "command": args.command,
        "exit_code": args.exit_code,
        "working_dir": args.working_dir or str(Path.cwd()),
        "tags": args.tags or [],
    }
    if args.result_summary:
        entry["result_summary"] = args.result_summary
    if args.error:
        entry["error"] = args.error

    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"Logged bash execution to {path}")
    return 0


def cmd_log_event(args: argparse.Namespace) -> int:
    """Log an arbitrary event (for HPC jobs, etc.)."""
    project_dir = args.project_dir or "."
    local_dir = ensure_project_store(project_dir)
    queue_dir = local_dir / "queue"

    ts = datetime.now(timezone.utc).isoformat()
    fname = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S_%f.jsonl")
    path = queue_dir / fname

    entry = {
        "timestamp": ts,
        "event_type": args.event_type,
        "data": json.loads(args.data or "{}"),
    }

    with open(path, "w") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"Queued event to {path}")
    return 0


def cmd_sync_queue(args: argparse.Namespace) -> int:
    """Ingest queued events from HPC jobs into the local session log."""
    project_dir = args.project_dir or "."
    local_dir = ensure_project_store(project_dir)
    queue_dir = local_dir / "queue"
    sessions_dir = local_dir / "sessions"

    if not queue_dir.exists():
        print("No queue directory found.")
        return 0

    fname = datetime.now(timezone.utc).strftime("%Y-%m-%d.jsonl")
    session_path = sessions_dir / fname

    ingested = 0
    for queued_file in sorted(queue_dir.glob("*.jsonl")):
        with open(queued_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                with open(session_path, "a") as out:
                    out.write(line + "\n")
                ingested += 1
        if args.delete_after:
            queued_file.unlink()

    print(f"Ingested {ingested} events into {session_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="compchem-memory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # log-bash
    p_bash = subparsers.add_parser("log-bash", help="Log a bash command")
    p_bash.add_argument("--project-dir", default=".")
    p_bash.add_argument("--command", required=True)
    p_bash.add_argument("--exit", type=int, dest="exit_code", default=0)
    p_bash.add_argument("--working-dir", default=str(Path.cwd()))
    p_bash.add_argument("--result-summary", default="")
    p_bash.add_argument("--error", default="")
    p_bash.add_argument("--tags", nargs="*", default=[])
    p_bash.set_defaults(func=cmd_log_bash)

    # log-event
    p_event = subparsers.add_parser("log-event", help="Log an arbitrary event")
    p_event.add_argument("--project-dir", default=".")
    p_event.add_argument("--event-type", required=True)
    p_event.add_argument("--data", default="{}")
    p_event.set_defaults(func=cmd_log_event)

    # sync-queue
    p_sync = subparsers.add_parser("sync-queue", help="Ingest queued HPC events")
    p_sync.add_argument("--project-dir", default=".")
    p_sync.add_argument("--delete-after", action="store_true")
    p_sync.set_defaults(func=cmd_sync_queue)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
