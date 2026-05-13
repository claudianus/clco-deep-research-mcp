---
name: Targeted Web Search
id: web-search
description: >
  Perform fast, targeted web searches with engine selection and
  result filtering. Use for quick fact-checking, finding specific
  resources, or discovering new tools and libraries.
triggers:
  - Quick fact-checking
  - Finding specific documentation pages
  - Discovering new tools or libraries
  - Checking latest versions of dependencies
  - Finding code examples for specific patterns
---

# Targeted Web Search

## When to Use

Use `web_search` when you need **quick, targeted results** (not deep synthesis):
- Fact-checking: "What is the latest Python version?"
- Finding docs: "FastAPI middleware documentation"
- Version checks: "urllib3 latest version PyPI"
- Code examples: "Python asyncio semaphore example"
- Discovering tools: "Python web scraping libraries 2026"

**web_search** returns faster (2-3s) than **deep_research** (5-15s) but with less synthesis.

## Engine Selection

| Engine | Strengths | Use When |
|--------|-----------|----------|
| `duckduckgo_lite` | Fast, reliable, default | General queries, default choice |
| `google` | Comprehensive, recent | Cutting-edge topics, recent news |
| `bing` | Locale-pinned, stable | Region-specific queries |
| `baidu` | Chinese content | Chinese language searches |
| `naver` | Korean content | Korean language searches |
| `ecosia` | Eco-friendly, European | European-focused content |
| `startpage` | Privacy, Google proxy | Privacy-sensitive searches |
| `yahoo` | Redirect decoding | Fallback when others fail |

**Auto-selection:** Use `engine="auto"` to let the registry pick the best engine based on query characteristics and current health.

## How to Use

### Basic search

```python
results = await web_search(
    query="Python 3.12 new features",
    engine="duckduckgo_lite",
    max_results=5,
)
```

### Engine failover

If one engine fails, the registry automatically tries the next:

```python
# If Google is rate-limited, auto-falls back to Bing, then DuckDuckGo
results = await web_search(
    query="FastAPI tutorial",
    engine="google",  # May fallback automatically
    max_results=5,
)
```

### Interpreting results

```markdown
1. **What's New In Python 3.12** [1]
   https://docs.python.org/3/whatsnew/3.12.html
   Python 3.12 brings improved error messages, type parameter syntax...
```

**Quality signals in results:**
- `🔒 authority` = Official/trusted source
- `📌 primary` = First-hand source
- `[1]`, `[2]` = Citation IDs for referencing

## Result Filtering

Results are automatically filtered for:
- **Spam domains** (known low-quality sites removed)
- **Duplicates** (same URL from multiple engines deduplicated)
- **Authority scoring** (low-authority results ranked lower)

You can further filter by source type:
- `official_docs` — Official documentation
- `github_repo` — GitHub repositories
- `blog_review` — Technical blogs
- `forum` — Stack Overflow, Reddit, etc.

## Common Mistakes

- ❌ Using `web_search` when `deep_research` is needed (complex topics)
- ❌ Not specifying `max_results` (defaults to 5, may need more)
- ❌ Ignoring engine health (check if engine is rate-limited)
- ❌ Trusting results without `fetch_page` verification
- ❌ Not using citation IDs when referencing sources

## web_search vs deep_research

| | web_search | deep_research |
|---|-----------|---------------|
| **Speed** | 2-3s | 5-15s |
| **Depth** | Raw results | Synthesized answer |
| **Citations** | Basic | Rich with scores |
| **Use for** | Quick lookup | Complex investigation |
| **Engines** | 1 | Multiple + ranking |
| **Output** | List of results | Structured markdown |
