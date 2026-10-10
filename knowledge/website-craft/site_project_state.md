---
id: site_project_state
label: Project state and approvals
type: process
stages: brief, direction, copy, sample, build, review, handoff
aliases: state file, resume, where were we, approvals, pick up where we left off, what stage
links:
- site_stage_brief | serves | Every stage reads and updates the state.
- decision_rights | uses | Approvals belong to Matthew, as the business graph says.
---
Every site project keeps a small state file so work resumes at the right stage without asking twice: .theseus/site-state.json in the project folder.

It holds:
- stage: brief, direction, copy, sample, build, review or handoff
- approvals: for each gate, who approved, when, and what exactly (file and version)
- decisions: the chosen route, fonts, palette, hero composition, primary action label
- open questions and blockers (missing photos, unconfirmed prices)

Do:
- Read the state file first, every session. Resume at its stage.
- Write a gate's approval only when Matthew actually approved it in words.
- When a later change touches an approved decision (new palette after the sample), say so and ask; do not silently re-open a gate.

Avoid:
- Treating silence, time passing, or "looks fine I guess" from yourself as approval.
- Re-asking for an approval that is recorded.

Check: the state file names the stage you are working in, and every gate behind you has an approval line.

Example:
{"stage": "sample", "approvals": {"brief": "Matthew 2026-10-12 brief.md v2", "direction": "Matthew 2026-10-12 route B"}, "decisions": {"route": "B workbench", "primary_action": "Book a tune-up"}}

Sources: Codex review of the Theseus upgrade (resume without repeating approvals). Checked 2026-10-10.
