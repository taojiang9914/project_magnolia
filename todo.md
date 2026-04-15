# Project Magnolia TODOs

This file tracks the **development and infrastructure** of the Magnolia agentic system itself, not individual research projects.

## Infrastructure & Agent Behavior
- [ ] Evaluate impact of growing `rules/*.md` files on agent context saturation
  - Monitor as more domain-specific rules are added (target: review when >15 files or any file >300 lines)
  - Consider mitigation: consolidate into `AGENTS.md`, tag-based loading, or rule summary layer
- [ ] Verify whether session and project memory entries have clear pathways for promotion to the skill tier
  - Document the promotion criteria and human-gating process
  - Test a concrete example of session → project → skill promotion
