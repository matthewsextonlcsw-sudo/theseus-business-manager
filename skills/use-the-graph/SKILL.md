---
name: use-the-graph
description: Look up the knowledge graphs before answering any business question (sales, pricing, follow-up, marketing, delivery, cash, reviews, local visibility, regulated clients) or doing website work (one stage at a time). Returns the rules to apply and the answer format.
whenToUse: Any question about running, selling, marketing, pricing, delivering or building for the business; before drafting a proposal, follow-up, review reply, status note or site plan; and at the start of every website stage.
---

# Use the graph

Two graphs are loaded together: the business graph (the rules a practical business manager applies) and the website craft graph (how to build a distinctive, honest site, stage by stage). Read the relevant topics before answering, and cite them.

For website work, look up only the stage you are in:

```bash
python3 scripts/graph.py brief --stage <brief|direction|copy|sample|build|review|handoff> "<the client and the question>"
python3 scripts/graph.py stages
```

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

3. For business questions, answer in this shape (website stages follow their own stage topic instead):
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
