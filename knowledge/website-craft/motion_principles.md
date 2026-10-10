---
id: motion_principles
label: Motion - one good moment, not many
type: craft
stages: direction, build, review
aliases: animation, motion, transitions, scroll animation, parallax, hover effects, micro interactions, gsap, reduced motion
links:
- design_read | uses | The motion dial sets how much moves.
- interaction_states | relates | Motion that answers a person's action is welcome.
- accessibility | constrains | Reduced motion is respected.
---
Motion should explain something or mark one deliberate moment. Scattered effects on every section are an AI tell.

Do:
- Let the motion dial decide the amount. Trust-first clients: almost none.
- One orchestrated moment beats many: one page-load sequence or one reveal.
- Motion that answers an action is welcome: a menu opening, a form confirming, a button pressing.
- Durations about 150-300 ms for interface changes, with an ease-out curve, starting from an already-visible state.
- Animate transform and opacity. List the properties; never transition: all.
- Button press feedback: scale to about 0.96, never below 0.95.
- Provide a prefers-reduced-motion version that removes movement.
- Content is fully visible without JavaScript and without animation.
- Autoplaying video only when muted, non-essential, and with a pause button (anything moving over 5 seconds needs one).

Avoid:
- Fade-and-slide-up on every section; hover lift on every card.
- Scroll hijacking, parallax and pinned scroll as defaults.
- Animation libraries for effects plain CSS can do.

Check: with reduced motion turned on, the page still makes sense and nothing moves on its own.

Sources: Anthropic frontend-design, one orchestrated moment (Apache-2.0); gogh motion doctrine resolution (Apache-2.0); emilkowalski/skills (MIT); Vercel Web Interface Guidelines, animations (MIT); WCAG 2.2 pause, stop, hide. Checked 2026-10-10.
