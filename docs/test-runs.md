# Test runs

Live runs of Theseus on real tasks, recorded as they happened. Paths and keys are removed.

## 2026-10-07: a regulated lead

- **Model:** Qwen3.8-Flash-Next, IQ3_XXS quant, served by Strata on a home GPU box
- **Harness:** DSH NEXT headless runner, with the standing brief plus the `business-manager` section, and the `use-the-graph` and `run-the-business` skills installed
- **Task:** "A therapist in Floral Park emailed asking for a new website with a chat bot on it. What do we do next? Keep it short."
- **What it did, unprompted:** loaded `use-the-graph`, ran `graph.py brief` twice (once for the lead, once for lead handling and pricing), and checked the local time
- **Time:** 77 seconds end to end
- **Checks passed:** used the four-part answer shape; applied `[regulated_clients]` (988/911, no clinical advice, no health details, no testimonials); refused to quote a price or start date; matched the lead to the right offers and their first deliverables; kept every outbound message behind the owner's approval

### Its answer

**Constraint.** Licensed clinical client, so `[regulated_clients]` wins: any chat on a therapy site must show emergency help (call/text 988 or 911), never give clinical advice, and collect no health details — chat, forms, or CRM. No solicited testimonials, no outcome guarantees. And `[studio_profile]` publishes no prices: **I can't quote or promise a start date — that's yours.**

**Next move.** First real reply tonight or tomorrow morning `[speed_to_lead]`. It asks for name, best contact, what they need, preferred time, and offers the next step — no price, no timeline. This lead hits two offers: **Websites and Search** (starts with a website and search brief) and **Managed AI** (starts with a use-case assessment and a go/no-go) `[studio_profile]`. It's 19:22 now; I'd send it first thing Thursday and log the lead.

**Failure mode.** Quoting a price in the reply, skipping the brief and starting design, or shipping a chat bot that answers clinical questions or collects health details.

**Measure.** Time from her email to first human reply, and whether she books the brief.

Two things from you: paste or forward her actual email so I can draft against what she asked, and your call on price. Want me to draft the reply now? Nothing goes out without your yes.
