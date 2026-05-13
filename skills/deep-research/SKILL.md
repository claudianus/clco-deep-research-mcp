---
name: Deep Research with maru-deep-pro-search
id: deep-research
description: >
  Conduct comprehensive, cited, multi-engine web research before making
  technical decisions. Use this skill to verify library versions, API docs,
  best practices, and security advisories with live web data instead of
  stale training knowledge.
triggers:
  - Before implementing new features
  - Before adding dependencies
  - Before proposing architecture changes
  - When training data cutoff is uncertain
  - For security or vulnerability assessment
---

# Deep Research

## When to Use

Your training data has a cutoff date. The web does not. Use `deep_research` when:
- Library versions or APIs may have changed since your knowledge cutoff
- Security advisories affect your dependencies
- You need current best practices (not 2023 patterns)
- Comparing alternatives (frameworks, tools, approaches)
- Writing documentation that references external resources

## How to Use

### Step 1: Formulate the query

Be specific. Include context that helps the search engines:

```
Good:  "FastAPI rate limiting middleware 2026 best practices"
Bad:   "FastAPI rate limiting"

Good:  "urllib3 CVE-2026-44431 patch version requirements"
Bad:   "urllib3 security"

Good:  "Python sentence-transformers vs openai embeddings accuracy benchmark 2026"
Bad:   "text embeddings comparison"
```

### Step 2: Call the tool

```python
result = await deep_research(
    query="your specific query",
    engine="auto",           # or specific: "duckduckgo_lite", "bing", "google"
    max_sources=10,          # 5-10 for most tasks, 15+ for deep investigation
    expand_queries=True,     # True for broad topics, False for narrow factual queries
)
```

### Step 3: Read primary sources

Use `fetch_page` on the top 2-3 results to verify claims:

```python
# From deep_research output, extract URLs
urls = extract_urls(result)
for url in urls[:3]:
    page = await fetch_page(url=url)
    # Verify version numbers, code examples, deprecation notices
```

### Step 4: Synthesize and cite

In your final output, always cite sources:

```markdown
According to the official documentation [1], FastAPI 0.115+
recommends `SlowAPIMiddleware` for rate limiting.

Sources:
[1] FastAPI Advanced Middleware — https://fastapi.tiangolo.com/advanced/middleware/
[2] slowapi GitHub — https://github.com/laurentS/slowapi
```

## Interpreting Results

The `deep_research` output includes quality signals:

| Signal | Meaning |
|--------|---------|
| `🔒 authority` | Official docs, GitHub repo, established blog |
| `📌 primary` | First-hand source (not aggregator) |
| `✓N engines` | Found by N independent engines (higher = more reliable) |
| `_score: 9.8` | Cross-engine BM25 + authority score (0-10) |

**Priority order for trusting sources:**
1. Official documentation (`🔒 authority` + `📌 primary`)
2. GitHub repositories (verified commits, recent activity)
3. High-scoring technical blogs (cross-engine confirmed)
4. Aggregators (Stack Overflow, Medium) — verify with primary source

## Benchmarked Performance

Verified against TREC-standard IR metrics (10 queries, ground-truth labeled):

| Metric | web_search (Bing 단일) | **deep_research (멀티 엔진)** | Improvement |
|--------|------------------------|------------------------------|-------------|
| Precision@5 | 0.140 | **0.260** | **+86%** |
| Precision@10 | 0.110 | **0.210** | **+91%** |
| Recall@10 | 0.600 | **1.000** | **+67%** |
| NDCG@10 | 0.488 | **0.668** | **+36%** |
| MRR | 0.483 | **0.603** | **+25%** |

**Trade-off**: Response time is ~2× slower (779ms → 1613ms) due to multi-engine search.

## Common Mistakes

- ❌ Using a single source without verification
- ❌ Ignoring the `🔒 authority` signal and trusting unverified blogs
- ❌ Not checking publication date (old best practices may be outdated)
- ❌ Skipping `fetch_page` on critical claims
- ❌ Forgetting to cite sources in final output
