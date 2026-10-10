---
id: site_stage_review
label: Stage 6 - Review and fix loop
type: process
stages: review
aliases: review the site, qa the design, screenshot review, polish, fix the design, self review, check my screenshots, looks bad
links:
- site_stage_handoff | next | Hand off only after the rubric passes and Matthew approves.
- visual_review_rubric | uses | Score from screenshots.
- looks_cheap_fixes | uses | Name each weakness and its repair.
- anti_slop | uses | Check for AI tells.
- browser_surfaces_polish | uses | The cheap details that show craft.
- site_qa_launch | uses | The business graph's QA checklist still applies.
---
Review in bounded rounds, not an endless loop: one full inspection, one batch of fixes, one confirming inspection. Then stop polishing and report.

Round:
1. Run the mechanical checks (qa script): overflow, broken media, contrast, fonts, forms, links.
2. Screenshot every page at 390 x 844 and 1280 x 800 (first screen and full page). Look at them. You can see images; use that.
3. Score the home page and one inner page with visual_review_rubric, citing what you see.
4. Name the three weakest visual decisions in plain words ("hero headline wraps to 4 lines on phone").
5. Fix all three in one batch, re-shoot, re-score.

Do:
- Judge from the screenshots, not from your memory of the code.
- Fix causes, not symptoms (a 4-line headline is a font-size or width error, not a copy error).

Avoid:
- Calling the first render finished.
- A third, fourth, fifth round of tiny tweaks. After the confirming round, report what is left.
- Claiming you saw a screenshot you could not open. Say "visual review pending" instead.

Check: rubric passes (26/30, nothing under 2, 3 on direction and hero) and every mechanical check is green.

Sources: impeccable "verify in bounded passes" (Apache-2.0); Anthropic frontend-design self-critique; taste-skill pre-flight. Checked 2026-10-10.
