---
id: mobile_composition
label: Phone layout
type: craft
stages: sample, build, review
aliases: mobile, phone layout, responsive, mobile first, small screen, tap targets, sticky button, mobile menu
links:
- hero_first_screen | checks | The phone first screen comes first.
- interaction_states | uses | Touch states and targets.
- site_qa_launch | refines | QA checks phone, tablet and desktop widths.
---
Most local customers arrive on a phone, often outside, often in a hurry. Design the 390 px screen first, then widen.

Do:
- Decide the stacking order on purpose for every multi-column section (what comes first on a phone, and why).
- Tap targets at least 44 px for main actions (WCAG's minimum is 24 px; local customers use thumbs).
- Phone numbers as tel: links, addresses as map links.
- For call or book businesses, consider a slim sticky action bar at the bottom; make sure it never covers content or form buttons.
- Form inputs at 16 px or larger so iPhones do not zoom.
- Crop pictures for portrait: set a focal point or a separate phone crop.
- Respect safe areas on notched phones.
- Check at 320 px too: nothing overflows sideways.

Avoid:
- Hiding the primary action in the menu.
- Hero images that push the headline below the first screen.
- Tiny text links as the main way to act.

Check: the 390 x 844 screenshot passes the first-screen rules; the 320 px view has no sideways scroll; every action is reachable with a thumb.

Sources: WCAG 2.2 target size minimum (w3.org/WAI/WCAG22/Understanding/target-size-minimum); Vercel Web Interface Guidelines, interactions (MIT); taste-skill mobile collapse rule (MIT). Checked 2026-10-10.
