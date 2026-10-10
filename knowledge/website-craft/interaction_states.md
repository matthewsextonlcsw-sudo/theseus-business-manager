---
id: interaction_states
label: Interaction states - every control, every state
type: craft
stages: build, review
aliases: hover, focus, active, disabled, loading state, error state, empty state, keyboard, focus ring, buttons, links
links:
- accessibility | refines | Keyboard and focus rules live there too.
- forms_that_convert | serves | Forms need the full set of states.
- motion_principles | uses | State changes may animate briefly.
---
AI builds tend to design only the resting, successful state. Every control needs its whole life.

Do:
- Hover, focus-visible, active (pressed), disabled, loading, error, and success, for every button, link and input.
- A visible focus ring that contrasts at least 3 to 1, shown for keyboard users (:focus-visible).
- Interactive states increase contrast compared with the resting state.
- Loading buttons keep their label and add a spinner or "Sending…".
- Links are links (<a>) and actions are buttons (<button>); never a clickable <div>.
- No dead zones: if part of a control looks clickable, all of it is.
- Hit area at least 24 px everywhere and 44 px for main actions.
- A skip link and a sensible tab order through the page.
- Empty and error states say what happened and what to do next.

Avoid:
- Removing focus outlines without a replacement.
- Disabled-looking buttons that are actually active, or the reverse.
- Hover-only information (phones cannot hover).

Check: tab through the page with the keyboard; every control shows focus and works; submit a form empty and with errors.

Sources: Vercel Web Interface Guidelines, interactions and forms (MIT); taste-skill interactive UI states (MIT); impeccable craft floor, states (Apache-2.0). Checked 2026-10-10.
