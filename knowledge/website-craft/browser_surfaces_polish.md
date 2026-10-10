---
id: browser_surfaces_polish
label: Finishing details the browser shows
type: craft
stages: build, review
aliases: polish, finishing touches, details, scrollbar, text selection, focus ring style, favicon, theme color, typographic quotes
links:
- interaction_states | relates | Focus rings are part of the finish.
- site_stage_review | serves | The review checks these.
---
The parts you did not draw still ship. Themed browser details are the cheapest sign that a site was built, not assembled.

Do:
- Text selection color from the palette (::selection).
- Focus rings styled from the palette, with offset, never removed.
- Link underline thickness and offset set on purpose.
- Scrollbar color matched to the theme where supported (scrollbar-color), especially on dark sites.
- color-scheme and the theme-color meta so phone browser bars match the page.
- Favicon and a social preview image in the brand.
- Typographic quotes (" ") and the ellipsis character (…), non-breaking spaces between numbers and units (20 min, $15).
- Tabular numbers for prices and hours in tables.
- No widows: one word alone on a headline's last line.
- A helpful 404 page in the site's design.

Avoid:
- Default blue links and default form controls on a designed page.
- Straight quotes and three dots in headlines.

Check: select some text, tab through, open the page on a phone with a dark browser bar, visit a broken link; every surface looks like the same site.

Sources: impeccable craft floor, browser surfaces (Apache-2.0); Vercel Web Interface Guidelines, content and design (MIT). Checked 2026-10-10.
