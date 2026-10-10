---
id: contrast_checks
label: Contrast checks
type: check
stages: direction, build, review
aliases: contrast, contrast ratio, readable text, text over image, wcag contrast, low contrast, button contrast
links:
- accessibility | refines | The business graph's accessibility rules apply.
- color_system | serves | Contrast is checked for every token pair.
---
Low contrast fails people and reads as cheap. Measure; do not eyeball.

The numbers (WCAG 2.2, level AA):
- Normal text: at least 4.5 to 1 against its background.
- Large text (24 px and up, or about 18.7 px bold and up): at least 3 to 1.
- Buttons, form borders, focus rings and icons that carry meaning: at least 3 to 1 against what is next to them.
- Placeholder and helper text is text: 4.5 to 1.

Do:
- Write the ratio next to each text pair on the direction board.
- Text over photos: put it on a calm area, a scrim (a dark gradient over the lower part) or a solid band. Check the worst spot, not the average.
- Make hover, focus and active states stronger than the resting state, never weaker.
- Pair color with a word or icon for status (do not rely on color alone).
- Check button text against the button, both states (a white button with white text is a real, common bug).

Avoid:
- Grey body text on a tinted background "for elegance".
- Thin weights at small sizes on dark backgrounds.

Check: run the accessibility scan; for text over images, inspect the screenshot and mark it for manual review when the tool cannot measure it.

Sources: WCAG 2.2 understanding docs for contrast minimum (w3.org/WAI/WCAG22/Understanding/contrast-minimum) and non-text contrast; taste-skill button and form contrast checks (MIT). Checked 2026-10-10.
