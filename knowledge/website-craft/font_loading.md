---
id: font_loading
label: Loading fonts fast
type: craft
stages: build, review
aliases: font loading, self host fonts, woff2, fontsource, font display, font flash, layout shift fonts, google fonts download
links:
- performance_budget | serves | Fonts count against the speed budget.
- type_pairing | serves | The chosen faces must arrive fast and right.
---
A beautiful face that arrives late costs speed and makes the page jump. Self-host and load only what the page uses.

Do:
- Self-host woff2 files (for example from the @fontsource packages or the Google Fonts download), not a third-party stylesheet.
- Load only the weights and styles in the tokens: usually 2-3 files total. Use a variable font if you need several weights.
- Subset to the scripts you use (Latin for most local sites).
- font-display: swap for body text; preload only the one or two faces used above the fold.
- Give the fallback similar metrics (size-adjust, ascent-override) so the swap does not shift the layout.
- Studio budget: about 200 KB of fonts in total. It is an internal target, not a web standard.
- Keep the font's license file in the project.

Avoid:
- Six weights "just in case".
- Preloading every font file.
- Loading fonts from a CDN the client does not control.

Check: in the browser, the screenshot shows the real faces (not the fallback); font transfer stays near the budget; no visible jump when fonts arrive.

Sources: web.dev font best practices (web.dev/articles/font-best-practices); Vercel Web Interface Guidelines, preload and subset fonts (MIT). Checked 2026-10-10.
