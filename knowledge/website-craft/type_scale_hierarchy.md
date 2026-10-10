---
id: type_scale_hierarchy
label: Type scale and hierarchy
type: craft
stages: sample, build, review
aliases: font size, headline size, type scale, hierarchy, heading sizes, line length, line height, h1 too small, h1 too big
links:
- type_pairing | uses | Sizes are chosen per face.
- hero_first_screen | serves | The hero headline is the biggest type decision.
- looks_cheap_fixes | fixes | Flat hierarchy is a top reason pages look cheap.
---
Hierarchy means a visitor sees the order of importance before reading a word. Make the steps obvious: headline, subhead, body, small print.

Do:
- Body text 16-18 px, line height about 1.5-1.65, lines of 45-75 characters.
- A fluid hero headline with clamp(), sized for the face and the words: roughly clamp(2.25rem, 6vw, 4.5rem) for 4-8 words, larger only for 2-4 words. Keep it to 2-3 lines on desktop.
- Display line height about 1.0-1.15. With italics, leave room for descenders (y, g, j, p).
- Tight tracking only at large sizes, and not below about -0.04em.
- More space above a heading than below it, so it belongs to what follows.
- text-wrap: balance on headings to avoid one-word last lines.
- Clear weight steps (for example 400 body, 600 subheads, 800 display), not five weights that look alike.

Avoid:
- A universal headline size. A 3-word headline and a 9-word headline need different sizes.
- Headlines over about 6rem on desktop; they turn into wallpaper.
- All-caps paragraphs and grey body text below contrast.

Check: on the desktop screenshot the H1 takes 2-3 lines and is clearly the largest text; on the phone it is still the largest and does not break mid-word.

Sources: impeccable craft floor and typeset (Apache-2.0); taste-skill hero font-scale discipline (MIT); Anthropic frontend-design line length (Apache-2.0); WCAG 2.2 (w3.org/TR/WCAG22). Checked 2026-10-10.
