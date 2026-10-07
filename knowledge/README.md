# Knowledge

Theseus's business knowledge is a small graph in JSON. Each **node** is one topic (sales, pricing, follow-up, website building, and so on) with the rules a practical expert would apply. Each **edge** says how two topics affect each other, with a sentence of context.

| File | What it is |
|---|---|
| `business-operating.v1.1.grag.json` | The original BusinessMasteryGraphRAG, kept unchanged |
| `business-operating.grag.json` | The current version Theseus uses (v1.2, in progress) |

## Shape

```json
{
  "graph_meta": { "name": "...", "version": "...", "usage": "...", "seed_hints": [{ "ask": "...", "seeds": ["node_id"] }] },
  "nodes": [{ "id": "pricing", "type": "skill", "label": "Pricing and discounts", "aliases": ["discount"], "knowledge": "..." }],
  "edges": [{ "source": "unit_economics", "target": "pricing", "relation": "constrains", "context": "..." }]
}
```

## How a model should use it

The graph is small enough (roughly 8-25K tokens) to give a model in full. When it grows past that, retrieve instead: match the question to `seed_hints` or to node labels and aliases, then follow edges one or two steps out. The `usage` field in `graph_meta` holds the answer rules. The most important ones: never invent numbers, use the business's own figures, and let `promise_integrity` and `unit_economics` overrule the rest.

## Checking it

```bash
python3 tools/check-graph.py knowledge/*.grag.json
```

The check fails on duplicate ids, edges or seed hints that name a missing topic, duplicate edges, and topics with no edges.
