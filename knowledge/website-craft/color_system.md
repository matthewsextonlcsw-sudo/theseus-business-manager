---
id: color_system
label: Color system
type: craft
stages: direction, sample, build
aliases: colors, palette, color scheme, brand colors, dark mode, light mode, accent color, background color
links:
- contrast_checks | needs | Every text pair is measured.
- design_fundamentals | refines | Neutrals, one accent, semantic colors.
- anti_slop | checks | Default palettes are a tell.
---
A palette is a system of surfaces, text and one accent, not a list of favorite colors. Name 4-6 tokens and use only those.

Do:
- Tokens: background, surface, raised surface, text, muted text, line, accent, and a soft tint of the accent. Add success, warning and error colors only where forms need them.
- One temperature of neutrals per site: warm greys or cool greys, never both.
- One accent, used the same way everywhere (actions and key highlights). A rose site does not get a teal button in the footer.
- Choose light or dark from where and when people look (a late-night bar menu, a bright clinic lobby), not from the category.
- Section tints within the same theme family are fine; one deliberate full inverse band is allowed if it marks a moment.
- Tint borders and shadows toward the surface color; shadows have offset and blur.
- Set color-scheme and the theme-color meta so browser chrome matches.

Palette families to rotate (pick by the business's world, do not reuse the last client's): forest green + bone + amber; off-black + warm tan; cobalt + one neutral; terracotta + cool slate; olive + brick + paper; monochrome + one saturated pop; silver-grey + smoke.

Avoid:
- Defaulting to cream + brass + espresso for "premium", or near-black + neon for "modern".
- Purple-blue gradients and glow as decoration.
- Saturated colors over about 80% saturation on large areas.

Check: list every color in the CSS; anything not in the tokens is a bug.

Sources: taste-skill color calibration and palette families (MIT); impeccable colorize and refuse list (Apache-2.0); Vercel Web Interface Guidelines, design (MIT). Checked 2026-10-10.
