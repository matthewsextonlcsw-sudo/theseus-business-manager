#!/usr/bin/env bash
# Standard-tier QA for one page, run in Theseus's own browser (agent-browser).
# Usage: qa.sh <url> [out-dir]
#   QA_REGULATED=1 qa.sh <url>   adds the checks for therapy and medical practices
# Exit codes: 0 = no failures, 1 = failures found, 2 = could not run.
set -uo pipefail

url="${1:?usage: qa.sh <url> [out-dir]}"
out="${2:-qa-$(date +%Y%m%d-%H%M%S)}"
mkdir -p "$out"
report="$out/report.txt"
: > "$report"

say() { echo "$*" | tee -a "$report"; }
here="$(cd "$(dirname "$0")" && pwd)"
browser="${THESEUS_BROWSER:-$here/../../browse-like-a-person/scripts/browser}"
[ -x "$browser" ] || browser="agent-browser"
ab() { "$browser" "$@" 2>/dev/null; }

command -v agent-browser >/dev/null || { echo "agent-browser is not installed"; exit 2; }
ab open "$url" >/dev/null || { echo "could not open $url"; exit 2; }
say "QA for $url ($(date '+%Y-%m-%d %H:%M'))"

# 1. Layout at phone, tablet and desktop widths
for spec in "390 844 phone" "768 1024 tablet" "1280 800 desktop"; do
  set -- $spec
  ab set viewport "$1" "$2" >/dev/null
  sleep 1
  wide=$(ab eval "document.documentElement.scrollWidth > document.documentElement.clientWidth" | tail -1)
  if [ "$wide" = "true" ]; then say "FAIL  sideways scroll at $3 width ($1px)"; else say "ok    no sideways scroll at $3 width ($1px)"; fi
  ab screenshot "$out/$3.png" >/dev/null && say "ok    screenshot saved: $out/$3.png (look at it)"
done

# 2. Accessibility, speed and page facts, read at desktop width
ab a11y --json > "$out/a11y.json"
ab vitals --json > "$out/vitals.json"
ab eval "JSON.stringify((() => {
  const text = document.body ? document.body.innerText : '';
  const fieldText = el => [el.name, el.id, el.placeholder, el.getAttribute('aria-label'), ...(el.labels ? [...el.labels].map(l => l.innerText) : [])].join(' ');
  const inputs = [...document.querySelectorAll('input:not([type=hidden]):not([type=submit]):not([type=button]), select, textarea')];
  return {
    title: document.title || '',
    description: (document.querySelector('meta[name=description]') || {}).content || '',
    lang: document.documentElement.lang || '',
    h1: document.querySelectorAll('h1').length,
    imgNoAlt: document.querySelectorAll('img:not([alt])').length,
    vagueActions: [...document.querySelectorAll('button, input[type=submit], a')].map(e => (e.innerText || e.value || '').trim().toLowerCase()).filter(s => ['submit', 'learn more', 'click here', 'read more'].includes(s)).length,
    placeholders: [/lorem ipsum/i, /your company/i, /your business name/i, /\\b555-\\d{4}\\b/, /\\[insert/i, /\\bTODO\\b/, /\\bTBD\\b/].filter(r => r.test(text)).map(String),
    unlabeledInputs: inputs.filter(i => !(i.labels && i.labels.length) && !i.getAttribute('aria-label') && !i.getAttribute('aria-labelledby')).length,
    healthFields: inputs.filter(i => /diagnos|symptom|medicat|condition|treatment|insurance id|date of birth|ssn/i.test(fieldText(i))).length,
    crisisNotice: /\\b988\\b/.test(text),
    jsonLd: document.querySelectorAll('script[type=\"application/ld+json\"]').length,
    thirdPartyScripts: [...new Set([...document.scripts].map(s => s.src).filter(Boolean).map(s => new URL(s, location.href).host).filter(h => h !== location.host))]
  };
})())" | tail -1 > "$out/page.json"
ab errors > "$out/console-errors.txt"

python3 - "$out" "${QA_REGULATED:-0}" <<'PY' | tee -a "$report"
import json, sys
from pathlib import Path

out, regulated = Path(sys.argv[1]), sys.argv[2] == "1"

def load(name):
    raw = (out / name).read_text().strip()
    data = json.loads(raw) if raw else {}
    return json.loads(data) if isinstance(data, str) else data

def line(kind, text):
    print(f"{kind:<5} {text}")

a11y = load("a11y.json").get("data", {})
violations = a11y.get("violations", [])
if violations:
    for v in violations:
        line("FAIL", f"accessibility: {v.get('id')} ({v.get('impact')}) on {v.get('nodeCount', len(v.get('nodes', [])))} elements - {v.get('help')}")
else:
    line("ok", f"accessibility: 0 violations, {a11y.get('counts', {}).get('passes', '?')} checks passed (axe {a11y.get('axeVersion', '?')})")
for item in a11y.get("incomplete", []):
    line("WARN", f"accessibility needs a human look: {item.get('id')} on {item.get('nodeCount', '?')} elements - {item.get('help')}")

vitals = load("vitals.json").get("data", {})
lcp = (vitals.get("lcp") or {}).get("startTime")
cls = (vitals.get("cls") or {}).get("score")
if lcp is None:
    line("WARN", "speed: no LCP reading")
elif lcp > 2500:
    line("FAIL", f"speed: LCP {lcp:.0f} ms (budget 2500)")
else:
    line("ok", f"speed: LCP {lcp:.0f} ms")
if cls is not None:
    line("FAIL" if cls > 0.1 else "ok", f"layout shift: CLS {cls:.3f} (budget 0.1)")

page = load("page.json")
checks = [
    (bool(page.get("title")), "FAIL", "page has a title"),
    (bool(page.get("description")), "FAIL", "page has a meta description"),
    (bool(page.get("lang")), "FAIL", "page declares its language"),
    (page.get("h1") == 1, "WARN", f"exactly one H1 (found {page.get('h1')})"),
    (page.get("imgNoAlt") == 0, "FAIL", f"every image has alt text ({page.get('imgNoAlt')} missing)"),
    (page.get("unlabeledInputs") == 0, "FAIL", f"every form field has a label ({page.get('unlabeledInputs')} unlabeled)"),
    (not page.get("placeholders"), "FAIL", f"no placeholder text ({', '.join(page.get('placeholders', [])) or 'none'})"),
    (page.get("vagueActions") == 0, "WARN", f"no vague buttons like Submit or Learn more ({page.get('vagueActions')} found)"),
    (page.get("jsonLd", 0) > 0, "WARN", "structured data present"),
]
if regulated:
    checks += [
        (page.get("healthFields") == 0, "FAIL", f"no form fields asking for health details ({page.get('healthFields')} found)"),
        (bool(page.get("crisisNotice")), "FAIL", "crisis notice with 988 is on the page"),
    ]
for passed, severity, text in checks:
    line("ok" if passed else severity, text)
third = page.get("thirdPartyScripts", [])
if third:
    line("WARN", "third-party scripts (each must earn its weight; never load trackers on a clinical site): " + ", ".join(third))

errors = (out / "console-errors.txt").read_text().strip()
line("WARN" if errors else "ok", "console errors: " + (errors.splitlines()[0][:160] if errors else "none"))
PY

fails=$(grep -c '^FAIL' "$report")
warns=$(grep -c '^WARN' "$report")
say "Summary: $fails failures, $warns warnings. Report: $report"
[ "$fails" -eq 0 ]
