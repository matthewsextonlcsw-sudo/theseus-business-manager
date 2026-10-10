---
id: site_stage_handoff
label: Stage 7 - Handoff and launch readiness
type: process
stages: handoff
aliases: handoff, deliver the site, launch, go live, launch record, finish the site
links:
- site_qa_launch | uses | The launch record format lives there.
- site_project_state | uses | Close the project state with every approval recorded.
- imagery_sourcing | checks | Every picture has a recorded source and license.
---
Deliver what Matthew needs to judge and run the site, and nothing that pretends to be more than it is.

Deliver:
- The preview link or local command.
- Phone and desktop screenshots of every page.
- The QA report and the final rubric scores.
- Picture credits: source, license, and "AI-generated" where true.
- Open issues, in order of importance.
- Editing guide: where the facts live (site.ts), where the tokens live, how to change a picture.
- The launch record (site_qa_launch) with today's date.

Do:
- Separate what you tested locally from what only a real launch can prove (forms reaching a person, search indexing, real-phone speed).
- Keep the business's accounts and files in the client's hands.

Avoid:
- Publishing or pointing a domain without Matthew's separate OK.
- Saying "done" while a check is failing or a picture is missing.

Check: someone who never saw the chat could take over the site from the handoff alone.

Sources: business graph site_qa_launch; Vercel Web Interface Guidelines, no dead ends (MIT). Checked 2026-10-10.
