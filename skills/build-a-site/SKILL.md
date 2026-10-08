---
name: build-a-site
description: Build a Standard-tier small-business website that is fast, accessible, honest and built to convert - brief, sitemap, real copy, design tokens, an Astro build from the starter, QA in your own browser, and a launch record. Premium custom design work is not this skill; hand that to Matthew.
whenToUse: Building, rebuilding or fixing a website or landing page for a client or for the studio.
---

# Build a site (Standard tier)

A Standard site is solid, clear and fast. It is not a custom design showpiece. It is never sloppy.

Before starting, pull the rules with `use-the-graph`: `[website_build_process]`, `[website]`, `[website_ia]`, `[copywriting]`, `[design_fundamentals]`, `[accessibility]`, `[performance_budget]`, `[site_qa_launch]`, `[seo_aeo_foundations]`, and `[local_visibility]` for local businesses. For therapy or medical clients, `[regulated_clients]` overrides the rest.

## The starter

Start every Standard site from `assets/starter` in this skill's folder (full path: `~/.dsh-next/skills/build-a-site/assets/starter`). Copy it into a new folder for the client inside your workspace, then run `npm install` there. Its `README.md` explains the parts. All business facts go in `src/data/site.ts`, and its `[insert ...]` placeholders make QA fail until every one is replaced. Set `regulated: true` for any clinical practice.

## The gates

Work in this order. At each gate, stop and show Matthew the file or the screenshots. Do not skip ahead.

1. **Brief** - fill in `references/brief-template.md` as `brief.md`. Gate: Matthew approves it.
2. **Sitemap** - every page with its one intent and one primary action, in `sitemap.md`.
3. **Copy** - real copy for every page in `content/`, from the brief and the client's own facts. Gate: Matthew approves the copy before any design.
4. **Tokens** - set the type scale, colors, spacing and radius in the starter's `src/styles/tokens.css`. Check every text color against its background.
5. **Build** - pages from the starter's components, mobile first. JavaScript only where a feature needs it.
6. **QA** - build (`npm run build`), serve it (`npm run preview`), run `scripts/qa.sh <url>` on every page (add `QA_REGULATED=1` for clinical practices), fix everything it reports, and run it again. Gate: show Matthew the screenshots and the QA report.
7. **Launch record** - fill in `references/launch-record-template.md` and hand it over with the accounts and docs.

## Never ship

If any of these is true, the site is not done:

- Lorem ipsum, "Your Company", placeholder phone numbers or addresses, TODO notes, test data
- Invented testimonials, reviews, numbers, awards or client logos; AI images of people who don't exist
- A first phone screen that doesn't say who it is for, the outcome, and the primary action
- Buttons that say "Submit" or "Learn more"; a form that doesn't reach a person; a form asking more than the next step needs
- Sideways scrolling on a phone; text over an image without enough contrast; body text under 16px
- Carousels, "Welcome to" headlines, autoplay video behind text, more than two typefaces, more than two button styles
- Missing alt text, unlabeled inputs, no visible keyboard focus, contrast below WCAG AA
- Images not sized for their slot, layout jumping while the page loads, third-party scripts loading before the content
- A name, address, phone or hours that don't match the Google Business Profile; missing titles or descriptions; structured data that says something the page doesn't
- Anything promising rankings, traffic or results
- For therapy or medical clients: testimonials, fields that ask for health details, promised outcomes, or a chat with no 988 / 911 notice

## Your browser

Use your own browser (the `browse-like-a-person` skill) to look at every page at phone, tablet and desktop widths. Read your screenshots before saying anything looks right. If you can't see it, you haven't checked it.

## Hand-off to Premium

If the client needs custom illustration, motion, a brand system, complex app features, or anything this checklist can't hold, say so in the brief and route it to Matthew as Premium work.
