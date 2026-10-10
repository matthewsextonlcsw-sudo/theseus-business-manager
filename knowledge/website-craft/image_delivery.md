---
id: image_delivery
label: Delivering pictures fast
type: craft
stages: build, review
aliases: image size, image format, avif, webp, srcset, lazy loading, lcp image, hero preload, image compression, layout shift images
links:
- performance_budget | serves | Pictures are most of the page's weight.
- hero_compositions | serves | The hero picture is usually the largest paint.
- browser_surfaces_polish | relates | Both are details that separate built from assembled.
---
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
