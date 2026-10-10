---
id: site_stage_build
label: Stage 5 - Full build
type: process
stages: build
aliases: build the site, full build, build all pages, implement the design, code the site
links:
- site_stage_review | next | Every build ends in the review loop.
- layout_grid_rhythm | uses | Section rhythm across whole pages.
- section_patterns | uses | Pick sections for their job, each layout family once.
- interaction_states | uses | Every control gets every state.
- font_loading | uses | Fonts load fast and do not shift the page.
- image_delivery | uses | Every picture is sized and delivered right.
- web_stack | uses | The business graph's stack rules apply (Astro, little JavaScript).
---
Apply the approved tokens, pictures and section plan to every page. Keep the sample's level: the last page should look as considered as the hero.

Do:
- Use the tokens only. A new color, font, radius or shadow that is not in the tokens is a bug.
- Choose sections from the copy plan, not from the starter's component list. Omit a section that has no real content.
- Vary layout families down the page (layout_grid_rhythm). No more than two image-text splits in a row.
- Build mobile first, and declare what every multi-column section does under 768px.
- Make every link, button and form work, with hover, focus, active, disabled, loading and error states.
- Keep JavaScript to features that need it.

Avoid:
- Filling every component the starter offers.
- Letting quality drop on inner pages (services, visit, privacy).

Check: open each page at phone and desktop width; nothing overflows sideways; every action works.

No gate here: the next stop is the review loop.

Sources: taste-skill layout discipline (MIT); Vercel Web Interface Guidelines (MIT); impeccable craft floor (Apache-2.0). Checked 2026-10-10.
