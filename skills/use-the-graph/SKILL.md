---
name: use-the-graph
description: Look up the business knowledge graph before answering any business question (sales, pricing, follow-up, marketing, delivery, cash, reviews, local visibility, websites, regulated clients). Returns the rules to apply and the answer format.
whenToUse: Any question about running, selling, marketing, pricing, delivering or building for the business, and before drafting a proposal, follow-up, review reply, status note or site plan.
---

# Use the graph

The business knowledge graph holds the rules a practical business manager applies. Read the relevant topics before answering, and cite them.

## Steps

1. Run the lookup with the question in plain words:

   ```bash
   python3 scripts/graph.py brief "<the question>"
   ```

   `scripts/` is in this skill's folder. If the relative path fails, use `~/.dsh-next/skills/use-the-graph/scripts/graph.py`.

2. If a topic in the output needs more depth, read it in full or see its links:

   ```bash
   python3 scripts/graph.py node pricing
   python3 scripts/graph.py expand pricing
   python3 scripts/graph.py list
   ```

3. Answer in this shape:
   - **Constraint:** what is actually holding this back
   - **Next move:** one concrete action, with an owner and a date
   - **Failure mode:** the mistake to avoid
   - **Measure:** the number or event that shows the move worked

   Cite topics in brackets, for example `[pricing]`, `[follow_up]`.

## Rules

- `[promise_integrity]`, `[unit_economics]` and `[decision_rights]` overrule the other topics. For licensed or medical clients, `[regulated_clients]` overrules them too.
- Never invent numbers: CAC, LTV, conversion rates, revenue, prices or ranking effects. Ask Matthew for the business's own figures, or say the number is unknown.
- Facts about the business come only from `[studio_profile]`. Prices, discounts, start dates and availability always go to Matthew.
- If the graph has nothing on the question, say so and give your best reasoning labeled as your own, not as the graph's.
