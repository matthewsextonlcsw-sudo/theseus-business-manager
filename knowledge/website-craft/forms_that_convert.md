---
id: forms_that_convert
label: Forms that people finish
type: craft
stages: build, review
aliases: contact form, booking form, quote form, form design, form fields, form errors, lead form
links:
- interaction_states | uses | Forms need every state.
- cro | refines | Ask only what the next step needs.
- regulated_clients | constrains | Clinical forms never ask for health details.
---
A form is a conversation with a stranger. Ask only what the next step needs, and make every error easy to fix.

Do:
- Fewest fields that let a person reply: usually name, a way to reply (email or phone), and one open question.
- Labels above inputs, always visible. Placeholders show an example, never replace the label.
- The right input types and autocomplete (email, tel, name) so phones show the right keyboard and autofill works.
- Errors next to their field, in words that say how to fix it; on submit, move focus to the first error. Keep what the person typed.
- Keep the submit button enabled until sending starts; then show "Sending…".
- After sending, say what happens next and when.
- The form works without JavaScript; with JavaScript it improves.
- Inputs at 16 px or larger on phones.

Avoid:
- "How did you hear about us", budget dropdowns, or a phone number required before any trust is earned.
- Blocking paste or typing.
- Health details, diagnoses or insurance numbers on any clinical form.

Check: fill the form on a phone, make each mistake once, and submit; every message is clear and nothing typed is lost.

Sources: Vercel Web Interface Guidelines, forms (MIT); taste-skill form patterns (MIT); business graph cro and regulated_clients. Checked 2026-10-10.
