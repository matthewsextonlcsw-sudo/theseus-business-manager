---
name: build-a-site
description: Build a small-business website that is distinctive, fast, accessible, honest and built to convert - seven stages with gates (brief, two directions, copy, rendered sample, build, review, handoff), each starting with its topics from the website craft graph, an Astro build from the starter, screenshots you actually look at, and a launch record.
whenToUse: Building, rebuilding or fixing a website or landing page for a client or for the studio.
---

# Build a site

Standard means a bounded scope: a small site, a fixed set of pages, the starter's stack. It never means a generic look. Every site gets a real art direction, a strong first screen with a real visual idea, and a review from screenshots.

## Every session

1. Read the project's state file, `.theseus/site-state.json` in the project folder (create it at the start; see `references/site-state.example.json`). Resume at its stage. Never re-ask for an approval that is recorded.
2. Look up ONLY the current stage's topics, and read every topic it prints:

   ```bash
   python3 ~/.dsh-next/skills/use-the-graph/scripts/graph.py brief --stage <stage> "<the client and your question>"
   ```

   `graph.py stages` lists the stages and their gates. `graph.py node <id>` reads one topic in full. The whole playbook is in `references/website-craft.md` if you need it.
3. Do the stage, write its file, and stop at its gate.

## The stages

| # | Stage | You produce | Gate |
|---|---|---|---|
| 1 | brief | `brief.md` from `references/brief-template.md` | Matthew approves it |
| 2 | direction | `direction.md`: two different routes, one recommended (`references/direction-board-template.md`) | Matthew picks a route |
| 3 | copy | `sitemap.md` and the page copy in `content/` | Matthew approves it |
| 4 | sample | the hero and the next section, built; screenshots at 390x844 and 1280x800; rubric scores | Matthew approves the look |
| 5 | build | every page | none: go straight to review |
| 6 | review | QA report, screenshots of every page, rubric, the three fixes | rubric passes and every check is green |
| 7 | handoff | handoff notes and `references/launch-record-template.md` filled in | publishing needs Matthew's separate OK |

Record every approval in the state file: who, when, and exactly what was approved. Silence is never approval.

## The starter

Start from `assets/starter` in this skill's folder (full path: `~/.dsh-next/skills/build-a-site/assets/starter`). Copy it into a new folder for the client inside your workspace, then run `npm install` there. Its `README.md` explains the parts. All business facts go in `src/data/site.ts`, and its `[insert ...]` placeholders make QA fail until every one is replaced. Set `regulated: true` for any clinical practice.

The starter's hero has no picture slot yet. When your route needs a picture (most do), add one the way `[hero_compositions]` and `[image_delivery]` describe: a responsive `<picture>`, width and height set, `fetchpriority="high"`, never lazy-loaded. Replace the starter's default tokens and system font with your route's type and palette.

## Pictures

Follow `[imagery_sourcing]`: the client's photos first. Generate only things that make no claim (objects, materials, textures, atmosphere); never people, and never the client's premises, work or products. Use the studio's picture maker: its command is in your AGENTS.md under **Pictures** (if none is listed, ask Matthew). Exit 0 = done, with the file's path on the last line; 3 = the studio is busy, try again later; 4 = it failed. Write an image brief first (`[image_art_direction]`) and record every picture in the project's picture manifest.

## Look at your work

Use your own browser (the `browse-like-a-person` skill) at phone, tablet and desktop widths, and run `scripts/qa.sh <url>` on every page (add `QA_REGULATED=1` for clinical practices). You can see images: open your screenshots and judge from them. Review in bounded rounds (`[site_stage_review]`): inspect, fix the three weakest things in one batch, confirm once, then report. If you could not see a screenshot, say "visual review pending". Never call a first render finished.

## Never ship

If any of these is true, the site is not done:

- Lorem ipsum, "Your Company", placeholder phone numbers or addresses, TODO notes, test data
- Invented testimonials, reviews, numbers, awards or client logos; AI pictures of people, or of the client's premises, work or products
- A first phone screen that doesn't show who it is for, the outcome, the primary action and a real visual idea
- A text-only hero with a button that the direction board did not deliberately choose; the system font as the headline face
- AI tells from `[anti_slop]` that the brief did not ask for
- Buttons that say "Submit" or "Learn more"; more than one wording for the primary action; a form that doesn't reach a person; a form asking more than the next step needs
- Sideways scrolling on a phone; text over an image without enough contrast; body text under 16px
- Carousels, "Welcome to" headlines, background video without a poster, a pause button and a scrim, more than two typefaces, more than two button styles
- Missing alt text, unlabeled inputs, no visible keyboard focus, contrast below WCAG AA
- Images not sized for their slot, layout jumping while the page loads, third-party scripts loading before the content
- A name, address, phone or hours that don't match the Google Business Profile; missing titles or descriptions; structured data that says something the page doesn't
- Anything promising rankings, traffic or results
- For therapy or medical clients: testimonials, fields that ask for health details, promised outcomes, or a chat with no 988 / 911 notice

## Premium work

Premium means a bigger scope, not better design: custom illustration, a full brand system, complex app features, booking or shop systems. Say so in the brief and route it to Matthew. Every site, Standard or Premium, gets a real direction.
