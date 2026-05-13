---
name: Comparative Parallel Search
id: parallel-search
description: >
  Run multiple search queries simultaneously and compare results.
  Use for technology comparisons, alternative evaluation,
  or gathering diverse perspectives on a topic.
triggers:
  - When comparing frameworks or libraries
  - When evaluating multiple approaches
  - When gathering diverse opinions on a topic
  - When writing comparison documentation
---

# Comparative Parallel Search

## When to Use

Use `parallel_search` when you need to **compare multiple things** simultaneously:
- Framework comparison: FastAPI vs Flask vs Django
- Library evaluation: sentence-transformers vs OpenAI embeddings
- Approach comparison: sync vs async patterns
- Tool evaluation: different search engines, databases, ORMs

**Why parallel?** Running queries sequentially takes N× longer. Parallel search runs all queries concurrently and produces a unified comparison table.

## How to Use

### Step 1: Define comparison queries

Each query should focus on ONE aspect of the comparison:

```python
queries = [
    "FastAPI async middleware performance benchmark 2026",
    "Flask async middleware performance benchmark 2026",
    "Django async middleware performance benchmark 2026",
]
```

### Step 2: Run parallel search

```python
result = await parallel_search(
    queries=queries,
    engine="duckduckgo_lite",
    max_results=5,
    comparison_mode=True,
)
```

### Step 3: Read the comparison table

The output includes:

```markdown
### Comparison Summary

| Query | Top Source | Type | Primary |
|-------|-----------|------|---------|
| FastAPI async | FastAPI docs | OFFICIAL-DOCS | ✓ |
| Flask async | Flask docs | OFFICIAL-DOCS | ✓ |
| Django async | Django docs | OFFICIAL-DOCS | ✓ |
```

### Step 4: Deep-dive on winners

Use `fetch_page` on the top source from each query to verify claims:

```python
# Extract top URLs from each query block
# Fetch each for detailed comparison
```

## Query Design Principles

| Bad | Good |
|-----|------|
| `"FastAPI vs Flask"` | `"FastAPI async performance benchmark 2026"` + `"Flask async performance benchmark 2026"` |
| `"best database"` | `"PostgreSQL vs MySQL performance benchmark 2026"` + `"PostgreSQL vs MySQL feature comparison 2026"` |
| `"Python web framework"` | `"FastAPI tutorial 2026"` + `"Flask tutorial 2026"` + `"Django tutorial 2026"` |

**Rule:** Each query should be **independently searchable** and **comparable**.

## Interpreting Results

The comparison table shows:
- **Top Source**: Best result for each query
- **Type**: `[OFFICIAL-DOCS]`, `[GITHUB-REPO]`, `[BLOG-REVIEW]`
- **Primary**: `✓` if the source is a primary/original source

**Decision framework:**
1. Prefer queries where top source is `OFFICIAL-DOCS` + `PRIMARY`
2. Check if multiple engines confirmed the same source (`✓N engines`)
3. Read the actual sources before drawing conclusions
4. Consider recency — newer sources may reflect latest versions

## Common Mistakes

- ❌ Vague comparison queries ("X vs Y")
- ❌ Too many queries (>5 becomes overwhelming)
- ❌ Ignoring the comparison table and reading all results manually
- ❌ Not verifying claims with `fetch_page`
- ❌ Drawing conclusions from a single source per query
