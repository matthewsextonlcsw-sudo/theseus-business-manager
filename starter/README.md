# Standard-tier site starter

The base Theseus builds small-business sites from, inside the `build-a-site` skill. Astro 7, plain CSS tokens, and no client-side JavaScript.

## What's in it

- `src/data/site.ts`: every business fact, once. It ships with `[insert ...]` placeholders, and the QA script fails until each one is replaced.
- `src/styles/tokens.css`: colors, type scale, spacing and shape. Set these to the client's brand; component styles read only tokens. The defaults are a neutral, contrast-checked baseline, not a finished design. The system font stack is a deliberate speed choice; add one brand face if the client has one.
- Pages: home, contact, privacy, 404, plus `sitemap.xml` and `robots.txt`.
- Structured data for the business type in `site.schemaType`, built from the same facts the page shows.
- A Content Security Policy built from the facts file, and security headers in `vercel.json`.
- `site.regulated = true` for clinical practices: shows the 988 / 911 crisis notice on every page, adds a "no health details" note to the form, and keeps testimonials off the page.
- The contact form appears only when `site.formAction` has somewhere to post. Otherwise visitors get a call button and an email link.

## Use

```bash
npm install
npm run build        # outputs dist/
npm run preview      # serves dist/ locally
bash ../skills/build-a-site/scripts/qa.sh http://localhost:4321/
```

`examples/site.example.ts` is a fictional dental practice for testing. Never ship it.
