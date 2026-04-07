"""Tests for compchem-memory: session, project, skill tiers."""

import json
import os
import tempfile
from pathlib import Path

import pytest
import yaml

from compchem_memory.tiers.session import SessionManager
from compchem_memory.tiers.project import ProjectManager
from compchem_memory.tiers.skill import SkillManager
from compchem_memory.learning.assessor import assess_run
from compchem_memory.learning.consolidator import consolidate_tier
from compchem_memory.index import MemoryIndex


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def project_dir(tmp_dir):
    pd = tmp_dir / "project"
    pd.mkdir()
    return pd


@pytest.fixture
def skills_dir(tmp_dir):
    sd = tmp_dir / "skills"
    sd.mkdir()
    return sd


class TestSessionManager:
    def test_record_and_get(self, tmp_dir):
        mgr = SessionManager(tmp_dir / "sessions")
        path = mgr.record("tool_call", {"tool": "haddock3", "args": {}})
        assert Path(path).exists()
        recent = mgr.get_recent()
        assert len(recent) == 1
        assert recent[0]["event_type"] == "tool_call"

    def test_search(self, tmp_dir):
        mgr = SessionManager(tmp_dir / "sessions")
        mgr.record("tool_error", {"error": "missing parameters"})
        mgr.record("tool_success", {"tool": "haddock3"})
        results = mgr.search("missing")
        assert len(results) == 1
        assert "missing" in results[0]["error"]

    def test_multiple_events(self, tmp_dir):
        mgr = SessionManager(tmp_dir / "sessions")
        for i in range(20):
            mgr.record("event", {"index": i})
        recent = mgr.get_recent(n=5)
        assert len(recent) == 5
        assert recent[-1]["index"] == 19


class TestProjectManager:
    def test_create_and_get_entry(self, project_dir):
        mgr = ProjectManager(project_dir)
        path = mgr.create_entry(
            str(project_dir), "Test Entry", "Content here", tags=["test"]
        )
        assert Path(path).exists()
        content = mgr.get_entry(str(project_dir), "Test Entry")
        assert content is not None
        assert "Content here" in content

    def test_list_entries(self, project_dir):
        mgr = ProjectManager(project_dir)
        mgr.create_entry(str(project_dir), "Entry A", "A content")
        mgr.create_entry(str(project_dir), "Entry B", "B content")
        entries = mgr.list_entries(str(project_dir))
        assert len(entries) == 2

    def test_search_entries(self, project_dir):
        mgr = ProjectManager(project_dir)
        mgr.create_entry(
            str(project_dir), "Haddock Note", "HADDOCK3 config", tags=["docking"]
        )
        results = mgr.search_entries(str(project_dir), keyword="HADDOCK")
        assert len(results) == 1

    def test_staging_and_confirm(self, project_dir):
        mgr = ProjectManager(project_dir)
        path = mgr.create_entry(
            str(project_dir), "Staged", "Staging content", staging=True
        )
        assert "staging" in path
        entries = mgr.list_entries(str(project_dir))
        assert len(entries) == 0

        mgr.confirm_staging(str(project_dir), "Staged")
        entries = mgr.list_entries(str(project_dir))
        assert len(entries) == 1

    def test_record_run(self, project_dir):
        mgr = ProjectManager(project_dir)
        path = mgr.record_run(
            str(project_dir),
            run_id="test_001",
            tool="haddock3",
            status="success",
            metrics={"score": -85.5},
        )
        assert Path(path).exists()
        history = mgr.get_run_history(str(project_dir))
        assert len(history) == 1
        assert history[0]["run_id"] == "test_001"


class TestSkillManager:
    def test_list_skills(self, skills_dir):
        (skills_dir / "HADDOCK3_SKILL.md").write_text(
            "---\nname: haddock3\nversion: 1.0\n---\n# HADDOCK3 Skill\n"
        )
        mgr = SkillManager(skills_dir)
        skills = mgr.list_skills()
        assert len(skills) == 1
        assert skills[0]["tool"] == "haddock3"

    def test_get_skill(self, skills_dir):
        (skills_dir / "HADDOCK3_SKILL.md").write_text(
            "---\nname: haddock3\n---\n# Content here\n"
        )
        mgr = SkillManager(skills_dir)
        content = mgr.get_skill("haddock3")
        assert content is not None
        assert "Content here" in content

    def test_search_skills(self, skills_dir):
        (skills_dir / "GNINA_SKILL.md").write_text(
            "---\nname: gnina\ntags: [covalent, docking]\n---\n# Gnina covalent docking\n"
        )
        mgr = SkillManager(skills_dir)
        results = mgr.search_skills(keyword="covalent")
        assert len(results) == 1


class TestAssessor:
    def test_assess_missing_dir(self):
        result = assess_run("/nonexistent/path", "haddock3")
        assert result["overall"] == "fail"
        assert result["technical"]["run_dir_exists"] is False

    def test_assess_with_output(self, tmp_dir):
        output = tmp_dir / "output" / "01_rigidbody"
        output.mkdir(parents=True)
        (output / "rigidbody_1.pdb.gz").write_text("fake")
        result = assess_run(str(tmp_dir), "haddock3")
        assert result["technical"]["run_dir_exists"] is True


class TestConsolidator:
    def test_consolidate_empty(self, project_dir):
        result = consolidate_tier("project", str(project_dir))
        assert result["merged"] == 0

    def test_consolidate_merges_duplicates(self, project_dir):
        mgr = ProjectManager(project_dir)
        mgr.create_entry(str(project_dir), "Same Title", "Content A")
        mgr.create_entry(str(project_dir), "Same Title", "Content B")
        result = consolidate_tier("project", str(project_dir))
        assert result["merged"] == 1


class TestMemoryIndex:
    def test_build_index(self, project_dir, skills_dir):
        (skills_dir / "HADDOCK3_SKILL.md").write_text(
            "---\nname: haddock3\n---\nContent\n"
        )
        mgr = ProjectManager(project_dir)
        mgr.create_entry(str(project_dir), "Test", "Content")

        idx = MemoryIndex(project_dir)
        entries = idx.build_index(
            project_dir=str(project_dir), skills_dir=str(skills_dir)
        )
        assert len(entries) == 2
        tiers = {e["tier"] for e in entries}
        assert tiers == {"skill", "project"}
