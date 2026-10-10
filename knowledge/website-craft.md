# Website craft playbook

Generated from `knowledge/website-craft/` by `tools/build_craft_graph.py`. Do not edit by hand.

For any agent that builds or reviews a website in this repo: follow the stages in order, read the topics for
the stage you are in, and stop at every gate for Matthew's approval. Theseus reads the same topics through
`skills/use-the-graph/scripts/graph.py brief --stage <stage> "<question>"`.

Rules that override everything here: never invent facts, reviews, people or pictures of the business
(promise_integrity); for therapists and clinics, the regulated-client rules win (regulated_clients).

## Stages and gates

| # | Stage | Topic | Gate |
|---|---|---|---|
| 1 | brief | site_stage_brief | Matthew approves brief.md |
| 2 | direction | site_stage_direction | Matthew picks one of two routes |
| 3 | copy | site_stage_copy | Matthew approves the sitemap and copy |
| 4 | sample | site_stage_sample | Matthew approves the rendered hero and next section |
| 5 | build | site_stage_build | no gate; go to review |
| 6 | review | site_stage_review | rubric passes and every check is green |
| 7 | handoff | site_stage_handoff | publishing needs Matthew's separate OK |

## Process

### Stage 1 - Brief and asset inventory (site_stage_brief)

Stages: brief

Before any design, write brief.md and get Matthew's approval. A site built on guesses looks generic because the guesses are generic.

Do:
- Name the business, who it serves, the outcome they buy, and the ONE primary action (call, book, visit, buy, get a quote).
- List confirmed facts only: services, prices, hours, address, phone, licenses, years in business. Mark anything unconfirmed as a question.
- Inventory assets and rights: photos (who took them, may we use them), logo, brand colors or fonts, existing site, Google Business Profile.
- Write the "design read" in one line (see design_read).
- Note constraints: regulated client, deadline, integrations, accessibility needs.
- Ask Matthew for 2-3 sites the client likes, and what they like about each.

Avoid:
- Starting from a template's sections and filling them in. Start from the business.
- Inventing anything to fill a gap. A gap is a question for Matthew.

Check: every fact in brief.md has a source; the primary action is one verb; missing assets are listed as blockers.

Gate: Matthew approves brief.md. Record it in the state file.

Sources: Anthropic frontend-design skill, "ground your designs in the subject matter" (github.com/anthropics/skills, Apache-2.0); taste-skill brief inference (github.com/Leonxlnx/taste-skill, MIT). Checked 2026-10-10.

Links: uses imagery_sourcing; uses site_project_state; next site_stage_direction; uses truthful_trust; refines website_build_process

### Stage 2 - Two directions to choose from (site_stage_direction)

Stages: direction

Show Matthew TWO genuinely different routes on one compact board, and recommend one. Two routes force a real decision; one route is a default in disguise.

Each route has:
1. A concept sentence tied to the business ("a workbench: honest tools, grease-dark surfaces, orange tags").
2. Three visual traits.
3. Two reference sites you actually opened, with one specific takeaway each.
4. Type system: display and body faces, or one family, with the reason.
5. Palette: 4-6 named hex values, with contrast ratios for text pairs.
6. Hero composition (from hero_compositions) and what picture it needs.
7. Imagery plan: source, style, subjects.
8. Phone plan: what the first phone screen shows.
9. One memorable detail that belongs to this business.

Do:
- Make the routes differ in composition, type and color, not just color.
- Write an ASCII sketch of each hero and the next section.
- Say which route you recommend and why, in one sentence.

Avoid:
- Two routes that are the same layout recolored.
- Routes that match an AI default (anti_slop): cream + serif + clay, near-black + one acid accent, the card kit.

Check: Matthew could tell the two routes apart from the concept sentences alone.

Gate: Matthew picks a route. Record the pick in the state file.

Sources: Anthropic frontend-design two-pass plan; impeccable new-work directions (github.com/pbakaus/impeccable, Apache-2.0). Checked 2026-10-10.

Links: checks anti_slop; uses art_direction; uses color_system; uses hero_compositions; next site_stage_copy; uses type_pairing

### Stage 3 - Sitemap and copy (site_stage_copy)

Stages: copy

Write sitemap.md and the real copy for every page before design spreads. Design without real copy is decoration around lorem ipsum.

Do:
- For each page: its one intent and its primary action.
- For each section: the visitor's question it answers, the answer, and the next action. If a section answers no question, cut it.
- Hero copy fits the first-screen rules (hero_first_screen): headline of 8 words or fewer, subtext of 20 words or fewer.
- Use the client's own facts and words. Prices only if confirmed.
- One label per intent across the whole site: if the action is "Book a tune-up", it is never also "Get started" or "Contact us".

Avoid:
- Sections that exist because the template had them (mission statement, "Why choose us" with three vague cards).
- Cute or "thoughtful-sounding" lines that say nothing. Plain beats clever.
- Invented numbers, reviews, awards or results.

Check: read only the headlines down the page; they should tell the story and lead to the action.

Gate: Matthew approves the copy. Record it in the state file.

Sources: taste-skill copy self-audit and content density (MIT); Vercel Web Interface Guidelines, content (github.com/vercel-labs/web-interface-guidelines, MIT). Checked 2026-10-10.

Links: uses copywriting; uses section_patterns; uses site_copy_voice; next site_stage_sample; uses website_ia

### Stage 4 - Rendered sample (hero plus next section) (site_stage_sample)

Stages: sample

Build only the hero and the next substantial section, in the chosen direction, with the approved copy and the real picture. Show Matthew screenshots at phone (390 x 844) and desktop (1280 x 800). A palette and a font list are not a design; pixels are.

Do:
- Set the design tokens first (type, color, spacing, radius), then build the two sections with them.
- Get the hero picture now (imagery_sourcing). If it cannot exist yet, say so; do not ship a gray box.
- Take the screenshots, look at them yourself, score them with visual_review_rubric, and fix the three weakest things before showing.
- Show the screenshots beside the direction board so Matthew can see the idea became a page.

Avoid:
- Building the whole site before this gate. A bad direction costs one section here and ten sections later.
- Showing a first render. The first render is a draft.

Check: on the phone screenshot, without scrolling, you can see who it is for, what they get, the action, and a real visual.

Gate: Matthew approves the look. Only then does it spread to every page.

Sources: Codex review of the Theseus upgrade (render, inspect, revise); Anthropic frontend-design self-critique with screenshots. Checked 2026-10-10.

Links: uses hero_first_screen; needs image_art_direction; checks looks_cheap_fixes; next site_stage_build; checks visual_review_rubric

### Stage 5 - Full build (site_stage_build)

Stages: build

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

Links: uses font_loading; uses image_delivery; uses interaction_states; uses layout_grid_rhythm; uses section_patterns; next site_stage_review; uses web_stack

### Stage 6 - Review and fix loop (site_stage_review)

Stages: review

Review in bounded rounds, not an endless loop: one full inspection, one batch of fixes, one confirming inspection. Then stop polishing and report.

Round:
1. Run the mechanical checks (qa script): overflow, broken media, contrast, fonts, forms, links.
2. Screenshot every page at 390 x 844 and 1280 x 800 (first screen and full page). Look at them. You can see images; use that.
3. Score the home page and one inner page with visual_review_rubric, citing what you see.
4. Name the three weakest visual decisions in plain words ("hero headline wraps to 4 lines on phone").
5. Fix all three in one batch, re-shoot, re-score.

Do:
- Judge from the screenshots, not from your memory of the code.
- Fix causes, not symptoms (a 4-line headline is a font-size or width error, not a copy error).

Avoid:
- Calling the first render finished.
- A third, fourth, fifth round of tiny tweaks. After the confirming round, report what is left.
- Claiming you saw a screenshot you could not open. Say "visual review pending" instead.

Check: rubric passes (26/30, nothing under 2, 3 on direction and hero) and every mechanical check is green.

Sources: impeccable "verify in bounded passes" (Apache-2.0); Anthropic frontend-design self-critique; taste-skill pre-flight. Checked 2026-10-10.

Links: uses anti_slop; uses browser_surfaces_polish; uses looks_cheap_fixes; uses site_qa_launch; next site_stage_handoff; uses visual_review_rubric

### Stage 7 - Handoff and launch readiness (site_stage_handoff)

Stages: handoff

Deliver what Matthew needs to judge and run the site, and nothing that pretends to be more than it is.

Deliver:
- The preview link or local command.
- Phone and desktop screenshots of every page.
- The QA report and the final rubric scores.
- Picture credits: source, license, and "AI-generated" where true.
- Open issues, in order of importance.
- Editing guide: where the facts live (site.ts), where the tokens live, how to change a picture.
- The launch record (site_qa_launch) with today's date.

Do:
- Separate what you tested locally from what only a real launch can prove (forms reaching a person, search indexing, real-phone speed).
- Keep the business's accounts and files in the client's hands.

Avoid:
- Publishing or pointing a domain without Matthew's separate OK.
- Saying "done" while a check is failing or a picture is missing.

Check: someone who never saw the chat could take over the site from the handoff alone.

Sources: business graph site_qa_launch; Vercel Web Interface Guidelines, no dead ends (MIT). Checked 2026-10-10.

Links: checks imagery_sourcing; uses site_project_state; uses site_qa_launch

### Project state and approvals (site_project_state)

Stages: brief, direction, copy, sample, build, review, handoff

Every site project keeps a small state file so work resumes at the right stage without asking twice: .theseus/site-state.json in the project folder.

It holds:
- stage: brief, direction, copy, sample, build, review or handoff
- approvals: for each gate, who approved, when, and what exactly (file and version)
- decisions: the chosen route, fonts, palette, hero composition, primary action label
- open questions and blockers (missing photos, unconfirmed prices)

Do:
- Read the state file first, every session. Resume at its stage.
- Write a gate's approval only when Matthew actually approved it in words.
- When a later change touches an approved decision (new palette after the sample), say so and ask; do not silently re-open a gate.

Avoid:
- Treating silence, time passing, or "looks fine I guess" from yourself as approval.
- Re-asking for an approval that is recorded.

Check: the state file names the stage you are working in, and every gate behind you has an approval line.

Example:
{"stage": "sample", "approvals": {"brief": "Matthew 2026-10-12 brief.md v2", "direction": "Matthew 2026-10-12 route B"}, "decisions": {"route": "B workbench", "primary_action": "Book a tune-up"}}

Sources: Codex review of the Theseus upgrade (resume without repeating approvals). Checked 2026-10-10.

Links: uses decision_rights; serves site_stage_brief

## Craft

### Art direction - choosing a world for the business (art_direction)

Stages: direction, sample

A distinctive site comes from the business's own world: its materials, tools, place and vocabulary. A bike shop has chain grease, steel, orange tags and hand-written tickets; a therapist has quiet rooms, daylight and plain speech. Build the look from that, not from "modern and clean".

Do:
- Find the most characteristic thing in the business's world and open the page with it (a real photo, an object, a headline in the business's own voice).
- Spend boldness in ONE place: one memorable detail (a tag-shaped price label, a hand-drawn route map, a big real photo). Keep everything around it quiet and disciplined.
- Let the world reach the whole page: the type, the surfaces and the picture style, not just one accent color on a neutral template.
- Write a concept sentence a non-designer understands.
- Before building, compare your plan to the generic page you would make for any similar business. Change whatever matches.

Avoid:
- "Modern, clean, professional" as a direction. That describes every template.
- Decoration that no part of the business explains.
- Copying another brand's identity. Borrow principles, never logos, layouts wholesale or images.

Check: hide the logo and name; could this page belong to a competitor? If yes, it has no direction yet.

Remove one accessory before you finish: cut the one decoration that serves nothing.

Sources: Anthropic frontend-design, "ground your designs in the subject matter" and "restraint" (Apache-2.0); impeccable worlds and comps (Apache-2.0). Checked 2026-10-10.

Links: checks anti_slop; refines design_fundamentals; uses hero_compositions; uses reference_analysis; serves site_stage_direction

### Finishing details the browser shows (browser_surfaces_polish)

Stages: build, review

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

Links: relates interaction_states; serves site_stage_review

### Color system (color_system)

Stages: direction, sample, build

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

Links: checks anti_slop; needs contrast_checks; refines design_fundamentals

### Design read and the three dials (design_read)

Stages: brief, direction

Before designing, state one line: "Reading this as: <kind of site> for <audience>, with a <feel> language." Then set three dials from 1 to 10. They keep a local model from defaulting to the same page every time.

- VARIANCE: 1 = strict symmetry, 10 = bold asymmetry and surprise.
- MOTION: 1 = static, 10 = cinematic.
- DENSITY: 1 = gallery-airy, 10 = packed with information.

Starting points for small-business sites (adjust from the brief):
- Trades and repair: variance 6, motion 3, density 5.
- Restaurant or cafe: variance 7, motion 4, density 4.
- Retail shop: variance 7, motion 4, density 5.
- Therapy or clinic: variance 3, motion 2, density 4.
- Professional services (law, accounting): variance 4, motion 2, density 5.
- Creative studio: variance 8, motion 6, density 3.

Do:
- Let the audience pick the feel, not your taste. A procurement panel and a design-conscious diner want different pages.
- Write the dials into the direction board and the state file.

Avoid:
- High motion for trust-first clients. Calm is the feature.
- The same dials for every client.

Check: the read names the audience, and the dials match the client type or say why not.

Sources: taste-skill brief inference and three dials (github.com/Leonxlnx/taste-skill, MIT); presets adapted for local businesses by MWS. Checked 2026-10-10.

Links: informs art_direction; informs layout_grid_rhythm; informs motion_principles; constrains regulated_clients

### Loading fonts fast (font_loading)

Stages: build, review

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

Links: serves performance_budget; serves type_pairing

### Forms that people finish (forms_that_convert)

Stages: build, review

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

Links: refines cro; uses interaction_states; constrains regulated_clients

### Hero compositions - seven to choose from (hero_compositions)

Stages: direction, sample

Choose one composition per route on the direction board. Each needs specific assets; check they exist before choosing.

1. Full-bleed photo with scrim: one wide photo of the place or the work in action, text over its calm area or a dark lower edge. Needs: a strong wide photo. Phone: crop to the focal point, text below the photo if it gets crowded.
2. Asymmetric split: text in about 5 of 12 columns, photo in 7, bleeding to the screen edge. Needs: one good photo. Phone: photo under the headline, never above an empty first screen.
3. Isolated object: one tool, product or dish, large, on a plain or textured ground. Needs: an object photo or a generated object with no people. Strong for repair, retail, food.
4. Editorial type: the headline itself is the visual, set big in a characterful display face. Needs: a great face and great words. Choose it on purpose; plain text with a button is not this.
5. Place-led: storefront, street or a drawn map beside address, hours and "Get directions". Needs: a real exterior photo or a map. For cafes and shops people visit.
6. Work-led: a strip or grid of real finished work. Needs: real project photos the client owns. For trades and studios.
7. Film hero: a poster image loads first, then a short muted loop with a pause button. Needs: real footage or an approved generated film. Matthew's own site uses this.

Avoid:
- Choosing a composition whose asset you do not have.
- Text over the busiest part of a photo.

Check: the direction board names the composition and its asset; the sample screenshot matches it.

Sources: gpt-taste hero options (taste-skill, MIT); impeccable comps (Apache-2.0); MWS site. Checked 2026-10-10.

Links: serves hero_first_screen; needs image_art_direction; needs image_delivery; checks mobile_composition

### Hero and the first screen (hero_first_screen)

Stages: copy, sample, build, review

The first screen decides whether a visitor stays. On a phone, without scrolling, it shows who the business is for, what they get, the action, and a real visual idea.

Do:
- Headline: 8 words or fewer, 2 lines on desktop (3 at most), in the business's specifics. Swap in a competitor's name; if the line still works, rewrite it.
- Subtext: 20 words or fewer, saying what happens or what they get.
- At most four text elements: optional small label, headline, subtext, actions (one primary, at most one secondary).
- Primary action visible on the phone without scrolling, in its working form where possible: a tap-to-call button, a booking slot, an "Order pickup" button.
- A real visual: the business's photo, a strong object, or a deliberately composed type treatment chosen on the direction board.
- Navigation on one line on desktop, about 64-72 px tall.
- Move trust strips, logos, prices and feature lists to the section below the hero.

Avoid:
- A tall empty gap above the headline (cap the top padding at about 6rem on desktop).
- Text over a busy photo with no scrim or calm area.
- Carousels, "Welcome to", stats rows, badges and pill tags in the hero.

Check: on the 390 x 844 screenshot, the four things are visible and readable without scrolling.

Sources: taste-skill hero discipline (MIT); impeccable persuade mode, "the action in its working form" (Apache-2.0); business graph website node. Checked 2026-10-10.

Links: uses hero_compositions; checks mobile_composition; uses primary_action_design; refines website

### Directing a picture - the image brief (image_art_direction)

Stages: direction, sample, build

One visual language per site: the same light, palette, angle and finish across every picture. Write an image brief before taking, choosing or generating any picture.

Image brief:
- Subject, and why it belongs to this business.
- Composition: angle (overhead, three-quarter, macro, wide), focal point, and which side stays calm for text.
- Light: soft daylight, hard workshop light, warm evening.
- Materials and textures: steel, linen, wood, paper.
- Palette: words that match the site's tokens.
- Crop: the slot's ratio (16:9 hero, 4:5 phone, 1:1 tile) and the phone crop.
- Exclusions: no people, no faces, no hands, no text, no logos, no watermarks.

Prompt pattern for the studio's picture maker:
"[subject], [angle] composition, focal point [left or right], calm empty area on the [side] for text, [light], [materials], [palette words], [mood]. No people, no hands, no text, no logos."

Do:
- Generate a few, pick the one that fits the brief, discard the rest.
- Keep text out of pictures; text belongs in the page so it stays readable and searchable.
- If the maker makes only squares, generate square and crop to the slot with a set focal point.

Avoid:
- Busy pictures behind headlines.
- Mixing photo styles (one moody, one bright, one illustrated) on one site.

Check: lay all the site's pictures side by side; they should look like one shoot.

Sources: taste-skill image strategy (MIT); Anthropic frontend-design (Apache-2.0); the studio's media runbook, picture maker (2026-10-09). Checked 2026-10-10.

Links: uses color_system; next image_delivery; uses imagery_sourcing

### Delivering pictures fast (image_delivery)

Stages: build, review

A great picture that loads slowly loses the visitor before it is seen.

Do:
- Use Astro's picture tools (astro:assets) or write srcset and sizes so each screen gets the right size.
- Serve AVIF or WebP with a JPEG fallback.
- Set width and height (or aspect-ratio) on every picture so nothing shifts as it loads.
- The hero (usually the largest paint): never lazy-load it; set fetchpriority="high". Preload it only if the browser finds it late (for example a CSS background), and use the responsive preload attributes so a second size is not downloaded.
- Every picture below the first screen: loading="lazy" and decoding="async".
- Studio budgets: about 200 KB for the phone hero and 350 KB for the desktop hero. These are internal targets, not web standards.
- Meaningful alt text; alt="" for purely decorative pictures.
- Video: a poster image first, then muted, playsinline, loading after the page, with a pause button.

Avoid:
- A 4000 px photo scaled down by CSS.
- Meaningful pictures as CSS backgrounds (no alt text, found late).
- Lazy-loading the hero.

Check: in the browser, the hero is one request at a sensible size; layout shift stays near zero; total picture weight on the home page is reasonable for a phone.

Sources: web.dev optimize LCP (web.dev/articles/optimize-lcp) and responsive images (web.dev/articles/serve-responsive-images); Vercel Web Interface Guidelines, performance (MIT). Checked 2026-10-10.

Links: relates browser_surfaces_polish; serves hero_compositions; serves performance_budget

### Where pictures come from - and what never to generate (imagery_sourcing)

Stages: brief, direction, sample, handoff

Pictures carry most of a site's quality, and every picture is also a claim. Get them in this order:

1. The client's own photos, with permission recorded (who took them, may we use them).
2. Commissioned photos (a short shoot by a photographer or by Matthew).
3. Generated pictures from the studio's picture maker, only for things that make no factual claim: textures, materials, tools or objects shown generically, abstract or atmospheric scenes. Its command is in Theseus's AGENTS.md under Pictures (exit 0 = done with the file path on the last line, 3 = the studio is busy, 4 = it failed).
4. Licensed stock, with the license recorded.

Never generate:
- People who do not exist: staff, owners, customers, patients.
- The client's premises, storefront, vehicles or team.
- Finished work or products shown as theirs ("our bikes", "our dishes").
- Before-and-after pictures of any kind.

Do:
- Record every picture in a manifest: file, source, license, and "AI-generated" where true.
- If the hero picture does not exist, it is a blocker: ask Matthew for it, or choose an editorial-type hero on the direction board on purpose.

Avoid:
- Random stock that any business could use.
- Placeholder grey boxes left in a delivered site.

Check: every picture in the build has a manifest line; no generated picture shows a person or poses as the business's real place, work or product.

Sources: business graph design_fundamentals and promise_integrity; taste-skill image strategy (MIT); the studio's media runbook (2026-10-09). Checked 2026-10-10.

Links: refines design_fundamentals; next image_art_direction; constrains regulated_clients; constrains truthful_trust

### Interaction states - every control, every state (interaction_states)

Stages: build, review

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

Links: refines accessibility; serves forms_that_convert; uses motion_principles

### Layout, grid and section rhythm (layout_grid_rhythm)

Stages: sample, build, review

Rhythm is what makes a scroll feel designed: sections change pace, size and density on purpose.

Do:
- One spacing scale (for example 4, 8, 12, 16, 24, 32, 48, 72, 96 px). Tight inside groups, generous between sections.
- Content width: about 1200-1380 px for the page, about 65 characters for reading text.
- Every element aligns to something: a grid column, a text edge or an optical center.
- Vary layout families down the page: full-bleed picture, split, list, gallery strip, band, map. Aim for 4 or more families on an 8-section page; avoid the same family twice in a row.
- At most two image-and-text splits in a row (no endless zigzag).
- Use cards only when elevation means something. Otherwise group with space or a line.
- One corner-radius rule for the whole site (all square, all soft, or a written rule such as "pill buttons, 12 px cards"). Nested corners are smaller than their parent.
- Higher variance dial: allow asymmetry (offset text, bleeding images). Lower: calm, even columns.

Avoid:
- Three equal cards as the answer to every section.
- A small label above every heading.
- "Big headline left, small paragraph right" section headers with nothing to say on the right.

Check: shrink the full-page screenshot until text is unreadable; you should still see changes in rhythm down the page.

Sources: taste-skill layout discipline (MIT); impeccable layout and craft floor (Apache-2.0); Vercel Web Interface Guidelines, layout (MIT). Checked 2026-10-10.

Links: fixes looks_cheap_fixes; serves mobile_composition; uses section_patterns

### Phone layout (mobile_composition)

Stages: sample, build, review

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

Links: checks hero_first_screen; uses interaction_states; refines site_qa_launch

### Motion - one good moment, not many (motion_principles)

Stages: direction, build, review

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

Links: constrains accessibility; uses design_read; relates interaction_states

### The primary action (primary_action_design)

Stages: copy, sample, build

Every page has one primary action, and it looks and reads the same everywhere on the site.

Do:
- Name what the visitor gets or does: "Book a tune-up", "Call the shop", "Reserve a table", "Get a free quote". One to three words is best; never wrap to two lines on desktop.
- One label per intent across the whole site (nav, hero, footer). "Contact us", "Get in touch" and "Let's talk" are one intent; pick one.
- Offer the action in its working form where possible: a tap-to-call link, a booking widget, an order button, not a link to a page that has another link.
- One primary button style, used only for the primary action. Secondary actions look clearly secondary.
- Repeat the action after proof and at the end of the page.
- Say what happens after the click ("We confirm by text within the hour"), and then make sure it is true.

Avoid:
- "Submit", "Learn more", "Click here".
- Two different primary actions competing in the hero.
- An arrow or icon on every button by habit.

Check: list every button label on the site; the primary intent has exactly one wording.

Sources: taste-skill CTA rules (MIT); impeccable persuade mode (Apache-2.0); Anthropic frontend-design writing (Apache-2.0); business graph website and cro. Checked 2026-10-10.

Links: refines cro; serves hero_first_screen; uses site_copy_voice

### Studying reference sites (reference_analysis)

Stages: brief, direction

References teach principles, not looks to copy. Open each one in your browser and write down specific, transferable observations.

Look at, and name concretely:
- Composition: where the eye lands first, how big the hero picture is, how text sits on it.
- Type: display face character, size jump from headline to body, line length.
- Spacing: how much room between sections, how tight groups are.
- Crop: how photos are framed (tight detail, wide place, object on plain ground).
- Color: how many colors, where the accent appears, light or dark.
- Density: words per section, how much is shown at once.
- Navigation and mobile: what happens at 390 px wide.

Do:
- Write one takeaway per reference as "Take X, because Y" ("Take the oversized real photo with a dark lower edge, because it makes the headline readable without a box").
- Include one or two local competitors to see what customers already compare against.
- Say plainly if you could not open a reference. Never describe a site you did not see.

Avoid:
- Copying layouts, logos, images, illustrations or copy. Those belong to the other brand.
- Vague notes ("clean, modern feel").

Check: every takeaway names something visible and a reason.

Sources: impeccable reference analysis (Apache-2.0); taste-skill reference signals (MIT). Checked 2026-10-10.

Links: informs art_direction; informs local_visibility; uses taste_references

### Section patterns - pick by the visitor's question (section_patterns)

Stages: copy, build

Every section answers one visitor question. If no question, no section. Choose from these and give each its own layout family.

- Proof strip (right under the hero): "Can I trust them?" Real facts: years, licenses, guarantees, process promises. No invented numbers.
- Services with prices: "What do they do and what does it cost?" A clear list or table with confirmed prices; better than icon cards.
- Split feature: "Tell me more about the main thing." One service in depth with its photo.
- Gallery strip: "Show me." Real work or the place, in one scrollable row or a tight grid.
- Process steps: "What happens if I book?" Numbered, because it is a real sequence.
- Owner or team: "Who will I deal with?" A real person and a real photo, or skip it.
- Location and hours: "Where and when?" Address, hours, map link, tap-to-call, directions.
- FAQ: "What about...?" Real questions customers ask; plain answers.
- Final action band: the one primary action again, with one line of reassurance.

Do:
- Order by the buyer's questions for that business type (see the pattern topics).
- Omit a section whose content does not exist yet; list it as a gap.

Avoid:
- "Why choose us" with three vague promises.
- Testimonials you do not have. Never invent them.
- Logo walls of companies that are not clients.

Check: write the visitor question next to each section in sitemap.md; every section has one.

Sources: taste-skill content density and section rules (MIT); business graph website and website_ia nodes. Checked 2026-10-10.

Links: uses layout_grid_rhythm; serves site_stage_copy; uses truthful_trust; refines website_ia

### Website copy that sounds like the business (site_copy_voice)

Stages: copy, review

Words are part of the design. Copy can make a page look as templated as any layout.

Do:
- Write from the customer's side, in plain words they use ("fix a flat", not "tire solutions").
- Specific beats clever: prices, times, places, names.
- Active voice; sentence case for headings and buttons on marketing pages.
- Headlines: 8 words or fewer in the hero, then one idea per section.
- Short sections: a headline of about 8 words and a paragraph of about 25 words, plus one picture or one action. More only when the section's job needs it.
- Keep the business's own vocabulary consistent: one name for each thing.
- Errors and empty states say what happened and how to fix it, without apology or vagueness.
- One voice per page; do not mix technical, poetic and salesy.

Self-audit before showing anything: re-read every visible string (headlines, buttons, alt text, footer, errors). Rewrite any line that is broken, vague, "thoughtful-sounding", or made of forced wordplay. Boring and true beats cute and wrong.

Avoid:
- Filler: "We are passionate about...", "Your trusted partner", "Elevate your...".
- Invented numbers or results.
- Accenting one word of a headline in another color or italic by habit.

Check: read the page aloud; every line says something a customer can use.

Sources: Anthropic frontend-design, writing in design (Apache-2.0); taste-skill copy self-audit (MIT); Vercel Web Interface Guidelines, copywriting (MIT). Checked 2026-10-10.

Links: checks anti_slop; refines copywriting; serves primary_action_design

### Trust without invented proof (truthful_trust)

Stages: brief, copy, build

Trust comes from specific, checkable facts. Invented proof is worse than none: it is a lie that a customer can catch.

Real proof to look for in the brief:
- Years in business, licenses and certifications (with numbers a customer can check).
- Guarantees and policies ("Flat fixed while you wait, or it's free").
- The owner's name and a real photo.
- Real reviews quoted with permission, linked to where they live.
- Process promises: what happens, when, and what it costs.
- Real photos of real work and the real place.

Do:
- Put a short factual proof strip right under the hero.
- Keep quotes to about three lines, with a real name and role.

Never:
- Invented testimonials, ratings, review counts, stats, awards or client logos.
- "Trusted by" walls of companies that are not clients.
- Fake people in pictures (see imagery_sourcing).
- Testimonials for therapists and clinicians (see regulated_clients).

Avoid:
- "Why choose us" cards with promises any competitor could make ("Quality", "Service", "Value").

Check: every proof item on the page has a source in brief.md.

Sources: business graph proof, promise_integrity and regulated_clients; taste-skill fake-precision and quotes rules (MIT). Checked 2026-10-10.

Links: constrains promise_integrity; refines proof; constrains regulated_clients; relates reviews_reputation

### Type pairing - fonts that fit the business (type_pairing)

Stages: direction, sample

The display face carries the page's personality; choose it from the business's world. One family is valid; two is a ceiling, not a score. If the client has brand fonts, use them first.

Starting pairings (all on Google Fonts under open licenses; check each font's license file before shipping):
- Barlow Condensed + Barlow: sturdy, mechanical. Trades, repair, gyms.
- Archivo Black + Work Sans: bold, workmanlike. Local services.
- Bebas Neue + Source Sans 3: loud, short headlines only (capitals). Events, fitness.
- Space Grotesk + DM Sans: modern, technical. Tech repair, small software.
- Outfit + Work Sans: geometric, friendly. General local business.
- Figtree + Noto Sans: clean, calm, readable. Clinics.
- Atkinson Hyperlegible (one family): built for legibility. Accessibility-first, therapy.
- EB Garamond + Lato: traditional, trustworthy. Law, accounting with heritage.
- IBM Plex Sans (one family): precise, steady. Finance, insurance.
- Playfair Display SC + Karla: elegant, menu-like. Restaurants.
- Rubik + Nunito Sans: rounded, approachable. Retail.
- Syne + Manrope: avant-garde. Creative studios.
- Bodoni Moda + Jost: high-end minimal. Boutiques.

Do:
- Pick for the business, then test with the real headline at real size.
- Use weight and size for emphasis inside the same family.

Avoid:
- The system font as the display voice of a client site.
- Inter as the first reach when nothing in the brief asks for neutral (it is fine for accessibility-first or public-sector briefs).
- A serif just because "premium". Choose serif when the world is editorial, heritage or culinary.
- Mixing a random second face into one headline word.

Check: the faces appear in the direction board with a reason, and the screenshot shows them loaded (not the fallback).

Sources: UI UX Pro Max typography data (github.com/nextlevelbuilder/ui-ux-pro-max-skill, MIT); gogh font-ban conflict resolution (Apache-2.0); taste-skill typography (MIT); Google Fonts FAQ (developers.google.com/fonts/faq). Checked 2026-10-10.

Links: checks anti_slop; refines design_fundamentals; needs font_loading; next type_scale_hierarchy

### Type scale and hierarchy (type_scale_hierarchy)

Stages: sample, build, review

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

Links: serves hero_first_screen; fixes looks_cheap_fixes; uses type_pairing

## Checks

### AI-made tells to avoid (anti_slop)

Stages: direction, sample, review

AI-built pages cluster around the same defaults. A visitor who has seen a hundred of them recognizes them at once. Any of these is fine when the brief asks for it; reaching for one when the brief leaves the choice free means nothing was decided.

The common clusters:
- Warm cream background, a high-contrast serif headline, a terracotta or clay accent.
- Near-black background with one acid-green, neon or vermilion accent.
- Purple or blue gradient hero with a glow.
- The card kit: everything in identical rounded cards, same soft shadow, three equal feature cards with icons.
- Template chrome: a small ALL-CAPS label above every heading, numbered markers (01 / 02 / 03) on things that are not a sequence, "A · B · C" meta strings, an arrow on every button, emoji as icons.
- One accented word in the headline (italic or a different color).
- Fade-and-slide-up on every section; hover lift on every card.
- Fake precision: invented stats, "98% satisfaction", fake logos, "Jane Doe" testimonials.
- Div-drawn fake screenshots and random blobs.

Do:
- Run this list against the direction board and against the screenshots.
- Replace a tell with a choice that comes from the business (art_direction).

Avoid:
- Swapping one cluster for another (cream-serif to neon-dark is still a default).

Check: count the tells on the page. More than one that the brief did not ask for is a failed review.

Sources: Anthropic frontend-design calibration list (Apache-2.0); taste-skill AI tells (MIT); impeccable refuse list (Apache-2.0). Checked 2026-10-10.

Links: fixes art_direction; relates looks_cheap_fixes; fixes type_pairing

### Contrast checks (contrast_checks)

Stages: direction, build, review

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

Links: refines accessibility; serves color_system

### Looks cheap - each failure and its fix (looks_cheap_fixes)

Stages: sample, review

Name the failure, then apply its fix. Fix the cause, not the symptom.

- Text-only hero with a button: the hero lacks a visual idea. Fix: a real photo or object (hero_compositions), or a deliberately composed type hero chosen on the direction board.
- System font as the headline: no voice. Fix: a self-hosted display face that fits the world (type_pairing).
- Small, timid headline: hierarchy is flat. Fix: a real size jump from headline to body, chosen per font (type_scale_hierarchy).
- 4-line headline on desktop: container too narrow or font too big. Fix: widen the container or lower the size; keep it to 2-3 lines.
- Everything centered: no tension. Fix: left-aligned text with an offset visual, unless centered was a chosen move.
- Every section the same layout: no rhythm. Fix: vary layout families; max two image-text splits in a row.
- Walls of equal cards: no hierarchy. Fix: one featured item large, the rest smaller, or a list without boxes.
- Generic headline ("Quality service you can trust"): swap in a competitor's name; if it still works, rewrite it with the business's specifics.
- Irrelevant stock picture: worse than none. Fix: the business's own subject, or a generated object or scene with no people.
- Gray text on gray, thin weights: low contrast. Fix: check ratios (contrast_checks).
- Default browser details (blue focus outline, gray scrollbar, raw form inputs): unfinished. Fix: browser_surfaces_polish.

Check: after fixing, re-shoot and confirm the failure is gone on phone and desktop.

Sources: impeccable bolder and craft floor (Apache-2.0); taste-skill layout discipline (MIT); Anthropic frontend-design (Apache-2.0). Checked 2026-10-10.

Links: fixes contrast_checks; fixes hero_first_screen; fixes layout_grid_rhythm; serves site_stage_review; fixes type_scale_hierarchy

### Visual review rubric (visual_review_rubric)

Stages: sample, review

Score each criterion 0-3 from the screenshots, citing what you see. 0 = broken or missing, 1 = generic or weak, 2 = intentional and solid, 3 = exceptional for this brief.

1. Business fit: it could only be this business. (3 = the world of the business is visible; 1 = any competitor could use it.)
2. Direction: distinctive and consistent. (3 = one clear idea, held everywhere; 1 = a template look.)
3. Hero and first screen: who, what, action, real visual on the phone. (3 = all four, striking; 1 = text and a button.)
4. Type and hierarchy: obvious order, characterful faces. (1 = system font, flat sizes.)
5. Imagery: relevant, one visual language, well cropped. (1 = generic stock or none.)
6. Section rhythm: varied families and pace. (1 = the same layout repeated.)
7. Color: one system, one accent, used consistently. (1 = random or default palette.)
8. Phone composition: designed for 390 px, thumb-friendly. (1 = a squeezed desktop.)
9. Copy and action: specific words, one clear action. (1 = filler and "Learn more".)
10. Finish: states, focus, browser details, no broken bits. (1 = defaults everywhere.)

Pass: 26 or more out of 30, nothing below 2, and 3 on Direction and Hero.

Rules:
- A good score never waives a factual, accessibility or function failure.
- Score only what you can see. If you cannot see the screenshot, write "visual review pending" and stop.
- Matthew's approval is still required; a self-score is not proof.

Sources: Codex review rubric (10 criteria); impeccable critique heuristic scoring (Apache-2.0); frontend-design-skill-benchmark method (reference only). Checked 2026-10-10.

Links: uses looks_cheap_fixes; serves site_stage_review; serves site_stage_sample

## Business patterns

### Pattern - therapists and clinical practices (pattern_clinical_practice)

Stages: brief, direction, copy

The visitor is often anxious and comparing quietly. They ask: will this person understand me, are they qualified, do they take my insurance, and how do I start without pressure.

First three sections, in order:
1. Hero: who the practice helps, in plain and warm words, and a low-pressure action ("Book a free 15-minute call"), with a calm real photo of the space or a quiet, non-human image.
2. Who it is for and what to expect: approaches in plain language, what the first session is like.
3. The clinician: name, license type and number, photo, a short human bio.
Then: fees and insurance, location or telehealth, FAQ, final action, the crisis notice.

Direction hints:
- Dials around variance 3, motion 2, density 4.
- Worlds: daylight, quiet rooms, natural materials, plain speech. Calm, not clinical-cold and not spa-cliche.
- Type: highly legible (Atkinson Hyperlegible, Figtree), generous size and spacing.

Must have:
- The 988 and 911 crisis notice.
- License details a visitor can verify.
- Fees or insurance stated plainly.

Never:
- Testimonials (professional codes discourage them), promised outcomes, before-and-after, or fields asking for symptoms or diagnoses.
- Generated pictures of people, sessions or the office.

Sources: business graph regulated_clients (NASW 4.07(b), HIPAA-minded intake); taste-skill trust-first dials (MIT). Checked 2026-10-10.

Links: uses design_read; constrains forms_that_convert; constrains regulated_clients; constrains truthful_trust

### Pattern - creative studios (pattern_creative_studio)

Stages: brief, direction, copy

The buyer judges the work first and the words second. They ask: is their style right for me, what have they made, and how do I start.

First three sections, in order:
1. Hero: the work itself, large, with one line of who the studio is for and how to start.
2. Selected work: a few strong projects, each with a short line of context, not everything.
3. How to work together: services, process and starting price or "from" price where confirmed.
Then: about, more work, contact.

Direction hints:
- Dials around variance 8, motion 6, density 3.
- Let the work lead: the interface recedes.
- One memorable interaction or layout move is welcome (a horizontal work strip, an unusual grid); keep it fast and accessible.
- Type: expressive display faces are allowed (Syne, a wide grotesk) when they match the studio's style.

Must have:
- Real work with credits and permission.
- Fast-loading galleries (image_delivery).

Avoid:
- Hiding the work behind long intro text.
- Showing everything; curate.

Sources: impeccable experience mode (Apache-2.0); taste-skill portfolio presets (MIT). Checked 2026-10-10.

Links: uses art_direction; uses hero_compositions; relates motion_principles

### Pattern - professional services (pattern_professional_services)

Stages: brief, direction, copy

The buyer is weighing risk: are you competent, will you understand my situation, what will it cost, and what happens first.

First three sections, in order:
1. Hero: the problem solved for whom, in plain words, and a clear first step (book a consultation, request a quote).
2. What you handle: practice areas or services, specific, with who each is for.
3. How it works and what it costs: the process in steps and how fees work.
Then: the people (real names, credentials, photos), proof (verifiable facts, published work), FAQ, final action.

Direction hints:
- Dials around variance 4, motion 2, density 5.
- Worlds: the desk, the document, the city, the ledger. Precise and steady, not stock-handshake.
- Type: an editorial or heritage serif can be right here (EB Garamond) when the firm's world is traditional; a precise sans (IBM Plex Sans) when it is modern.
- Hero: editorial type, chosen deliberately, or a split with a real portrait or the real office.

Must have:
- Real credentials and bar or license numbers where relevant.
- Required disclaimers (attorney advertising, financial disclosures) where they apply.

Avoid:
- Handshake and gavel stock photos.
- Vague promises ("results-driven", "client-focused").

Sources: business graph website, proof and promise_integrity. Checked 2026-10-10.

Links: uses hero_compositions; uses section_patterns; uses truthful_trust

### Pattern - restaurants and cafes (pattern_restaurant_cafe)

Stages: brief, direction, copy

The diner asks: what is it like, what can I eat, is it open now, and where is it. Atmosphere sells; hours and the menu close the deal.

First three sections, in order:
1. Hero: the feeling of the place and the action (reserve, order pickup, or get directions), with a real photo of the room or the food.
2. Hours and location, up high: open now or not, address, map link, phone.
3. The menu: real dishes and prices as text, never only a PDF or a photo of a menu.
Then: the story or the chef, gallery of the room and dishes, private events, final action.

Direction hints:
- Dials around variance 7, motion 4, density 4.
- Worlds come from the cuisine and the room: chalkboard, tile, linen, neon, wood, a street corner.
- Type with appetite: a characterful display face (menu-like or hand-lettered feel) with a clean body face.
- Hero: place-led or object focus with a real dish.

Must have:
- Menu as real text (readable, searchable, accessible).
- Hours that match the Google profile, including holidays.
- Reservation or ordering in its working form.

Avoid:
- Generated pictures of dishes or the room posing as theirs.
- Autoplay music.
- A PDF-only menu.

Sources: business graph local_visibility and website; impeccable persuade mode, the action in its working form (Apache-2.0). Checked 2026-10-10.

Links: uses hero_compositions; constrains imagery_sourcing; uses section_patterns

### Pattern - retail shops (pattern_retail_shop)

Stages: brief, direction, copy

The shopper asks: what do you sell, is it my style, can I buy it online or should I visit, and when are you open.

First three sections, in order:
1. Hero: the shop's point of view and the main way to buy (visit, order, call), with a real product or the real shop.
2. What they sell: a few featured categories or items with real photos and prices where confirmed.
3. Visit or buy: address, hours, parking or transit, pickup and delivery options.
Then: the story, new arrivals, events, FAQ, final action.

Direction hints:
- Dials around variance 7, motion 4, density 5.
- Worlds come from the goods: their materials, colors and the shop floor.
- Type: matches the goods (refined for boutiques, playful for gifts).
- Hero: object focus with one hero product, or place-led with the storefront.

Must have:
- Real product photos with consistent light and background.
- Clear "how to buy" (in store, pickup, shipping).

Avoid:
- Generated product pictures posing as stock the shop really has.
- A wall of identical product cards on the home page; feature a few.

Sources: business graph website; taste-skill content density (MIT). Checked 2026-10-10.

Links: uses hero_compositions; needs image_delivery; uses section_patterns

### Pattern - trades and repair shops (pattern_trades_repair)

Stages: brief, direction, copy

The buyer has a broken thing and a question: can you fix it, how much, how fast, and where. They are often on a phone, sometimes standing next to the problem.

First three sections, in order:
1. Hero: what you fix, for whom, and the action (call or book), with a real picture of the work, the tools or the shop.
2. Prices and turnaround: a clear list ("Basic tune-up $65, 2 days"). Prices and speed are the strongest proof a trade has.
3. Proof strip: years, licenses, guarantees, the owner's name.
Then: services in depth, real work gallery, location and hours, FAQ, final action.

Direction hints:
- Dials around variance 6, motion 3, density 5.
- Worlds: the workbench, the toolbox, the job ticket, the van. Honest materials (steel, grease-dark, kraft paper, safety colors) used with restraint.
- Type: sturdy or condensed faces (Barlow Condensed, Archivo Black) with a plain body face.
- Hero: object focus (one tool or part, big), work-led, or a full-bleed photo of real work.

Must have:
- Tap-to-call in the hero and a sticky call or book bar on phones.
- Service area named.
- Emergency or same-day info if it exists.

Avoid:
- Generic "quality craftsmanship" lines; say what you fix and how fast.
- Stock photos of smiling workers.

Sources: business graph website and local_visibility; MWS practice brief (Ridgewood Bike Works, 2026-10-09). Checked 2026-10-10.

Links: uses hero_compositions; relates local_visibility; uses section_patterns

## References

### Gold standard - what the MWS Consulting site does well (gold_standard_mws)

Stages: direction, review

Matthew's own site (mwsconsulting.studio) shows principles to transfer. Its look is the studio's brand; never clone its dark palette or neon onto a client.

What it does well:
- One signature idea tied to the story: a claymation film of owners going from tech overload to calm, behind a headline styled as glass neon tubes. The idea IS the offer.
- The hero picture loads first (a poster image with high fetch priority); the film loads after, muted, looping, with a pause button; a scrim keeps the text readable.
- A two-line, plain headline in the customer's words ("Less tech stress. More real work.") and one concrete sentence of what they do.
- Two actions: the main one, plus a free, low-risk first step.
- Right under the hero, a strip of factual commitments (owned work, a free first look, scope in writing, client-owned accounts) instead of testimonials it does not have.
- Local specificity: it names the towns it serves.
- Self-hosted display and body faces (Archivo Black and Inter), only the weights used, preloaded.
- A tight token set: three surface levels, one electric accent with a soft tint, one corner radius.

Transfer:
- Find the client's own story and make one visual idea of it.
- Load the hero picture first; anything heavy comes after.
- Replace missing testimonials with true commitments.

Check: when you cite this site, name the principle, not the colors.

Source: the MWS Consulting site, reviewed 2026-10-10.

Links: example_of art_direction; relates studio_profile; serves taste_references

### Matthew's taste references (taste_references)

Stages: brief, direction, review

This topic holds the sites Matthew likes and what he likes about each. It is his taste, recorded in his words. Never invent entries.

Seeded reference:
- Matthew's own site, MWS Consulting (see gold_standard_mws): a full-bleed film hero, a short two-line headline, a free first offer beside the main action, and a strip of factual commitments instead of testimonials.

Matthew's favorites (empty until he names them):
1. [site] - what he likes:
2. [site] - what he likes:
3. [site] - what he likes:
4. [site] - what he likes:
5. [site] - what he likes:

Do:
- Ask Matthew for 3-5 favorites at the first brief if this list is still empty, and record his exact words.
- Use his favorites as principles across clients, never as a theme to clone onto every site.
- When a client's brief conflicts with Matthew's taste, the client's brief wins for that client.

Avoid:
- Guessing his preferences from one comment.
- Turning his own brand (dark, electric cyan) into every client's palette.

Check: every entry has a source line (when and where Matthew said it).

Links: uses gold_standard_mws; informs reference_analysis

Sources: github.com/anthropics/skills (frontend-design, Apache-2.0); github.com/Leonxlnx/taste-skill (MIT); github.com/pbakaus/impeccable (Apache-2.0); github.com/vercel-labs/web-interface-guidelines (MIT); github.com/nextlevelbuilder/ui-ux-pro-max-skill (MIT); github.com/AgriciDaniel/gogh (Apache-2.0); github.com/emilkowalski/skills (MIT); w3.org/TR/WCAG22 and its understanding documents; web.dev (LCP, responsive images, font best practices). Checked 2026-10-10.
