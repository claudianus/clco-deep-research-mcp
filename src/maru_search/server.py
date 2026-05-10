from __future__ import annotations

import logging
import sys

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("maru-search")

_logger = logging.getLogger("maru_search")
_logger.setLevel(logging.INFO)

_stderr_handler = logging.StreamHandler(sys.stderr)
_stderr_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
)
_logger.addHandler(_stderr_handler)
_logger.propagate = False


# ═══════════════════════════════════════════════════════════════
# MCP Prompts — Universal Tool Selection Guidance
# ═══════════════════════════════════════════════════════════════

@mcp.prompt()
def tool_selection_guide() -> str:
    """Comprehensive guide for choosing the right research tool."""
    return """# Maru Search Tool Selection Guide

## Quick Decision Tree

```
What do you need?
├── Quick answer with sources?
│   └── answer (Perplexity-style)
│       └── Need deeper detail? → deep_research
│
├── Find information on a topic?
│   ├── Single angle → web_search
│   └── Multiple angles → parallel_search
│
├── Need citation-ready sources?
│   └── search_with_citations
│
├── Read specific URLs?
│   ├── One URL → fetch_page (try first)
│   │   └── Blocked? → fetch_page with stealth=True
│   │       └── Still blocked? → stealthy_fetch (last resort)
│   └── Multiple URLs → fetch_bulk
│
└── Deep research on unfamiliar topic?
    └── deep_research
        └── Too much output? → Use summarize=True
```

## Tool Details

### answer
**When to use**: You want a direct, cited answer like Perplexity.
**Example**: "What is quantum computing?"
**Returns**: Synthesized answer with inline citations [1], [2].
**NOT for**: Reading known URLs.

### web_search
**When to use**: You need to find sources on a single topic.
**Example**: "Python asyncio best practices"
**Returns**: Ranked results with [AUTHORITY] badges and citation IDs.
**NOT for**: Reading known URLs.

### search_with_citations
**When to use**: You need sources for academic/technical writing.
**Example**: Research paper background
**Returns**: Results pre-tagged with citation IDs [1], [2].

### parallel_search
**When to use**: You need multiple perspectives simultaneously.
**Example**: ["Python vs Go performance", "Python concurrency tutorial"]
**Returns**: Separate result sets for each query, merged output.

### fetch_page
**When to use**: You have a specific URL to read.
**Example**: "https://docs.python.org/3/library/asyncio.html"
**Returns**: Clean extracted content with quality signals.
**Anti-bot fallback**: If blocked, retry with stealth=True.

### fetch_bulk
**When to use**: You have 2-10 URLs from search results.
**Returns**: All pages in parallel with quality badges.

### deep_research
**When to use**: You need comprehensive research on an unfamiliar topic.
**Example**: "Explain Kubernetes networking to me"
**Returns**: Synthesized findings with citations and quality scoring.

### stealthy_fetch
**When to use**: fetch_page failed even with stealth=True.
**Example**: Cloudflare-protected sites
**Returns**: Same as fetch_page but with full browser automation.
**Warning**: ~3-5x slower. Use as last resort.

## Performance Ranking
1. **Fastest**: answer, web_search, fetch_page
2. **Medium**: parallel_search, fetch_bulk, search_with_citations
3. **Slow**: deep_research
4. **Slowest**: stealthy_fetch

## Common Mistakes
- ❌ Using stealthy_fetch for every URL
- ❌ Using deep_research for single-page reads
- ❌ Not checking quality badges ([HIGH], [BLOCKED])
- ❌ Ignoring follow-up links in results
- ❌ Not using citations when user asks for sources
"""


@mcp.prompt()
def anti_bot_strategy() -> str:
    """Step-by-step strategy for handling anti-bot protected sites."""
    return """# Anti-Bot Handling Strategy

## Escalation Ladder (try in order)

### Step 1: Normal Fetch
Use `fetch_page(url)`
- Fastest option
- Works for 70-80% of sites

### Step 2: Stealth Mode
If Step 1 returns [BLOCKED] or incomplete:
Use `fetch_page(url, stealth=True)`
- Enables basic anti-bot bypass
- Still relatively fast

### Step 3: Full Stealth
If Step 2 still fails:
Use `stealthy_fetch(url)`
- Full browser automation
- Bypasses Cloudflare Turnstile, DataDome
- ~3-5x slower

### Step 4: Accept Defeat
If all steps fail:
- The site may require JavaScript execution
- Try searching for the content on alternative sites
- Use `web_search` to find mirrors or cached versions

## When to Skip Steps

Skip directly to stealthy_fetch if:
- You know the site uses heavy protection (e.g., Cloudflare challenge page)
- You've failed on this domain before
- The content is critical and worth the wait

## Bulk Fetching with Mixed Results

When using fetch_bulk with multiple URLs:
1. Check quality badges in results
2. Re-fetch [BLOCKED] ones with stealth=True
3. If still blocked, use stealthy_fetch individually
"""


@mcp.prompt()
def research_workflow() -> str:
    """Recommended workflow for comprehensive research tasks."""
    return """# Research Workflow Template

## Phase 1: Discovery
**Goal**: Find relevant sources

1. Start with `answer(query)` for quick, cited overview
   - Review inline citations [1], [2]
   - Note promising URLs

2. OR use `deep_research(query)` for broad exploration
   - Let it auto-expand queries
   - Review quality badges ([HIGH] = prioritize)
   - Note promising URLs

3. OR use `parallel_search` for targeted angles:
   ```
   [
     "{topic} tutorial beginner",
     "{topic} best practices 2025",
     "{topic} common pitfalls"
   ]
   ```

## Phase 2: Deep Reading
**Goal**: Extract detailed information

1. Use `fetch_bulk(urls)` for all promising URLs
2. Check quality signals:
   - [HIGH] → Read fully
   - [med] → Skim for relevance
   - [BLOCKED] → Retry with stealth

3. For critical sources that failed:
   - `fetch_page(url, stealth=True)`
   - Or `stealthy_fetch(url)` as last resort

## Phase 3: Synthesis
**Goal**: Combine findings with proper citations

1. Review all fetched content
2. Use `search_with_citations` to find additional sources if needed
3. Cross-reference information across sources
4. Always cite sources using [1], [2] format when answering

## Token Management Tips

- **Default budgets are generous** (fetch_page: 6000 tokens)
- **Use summarize=True** in deep_research if output exceeds context window
- **Quality over quantity**: 3 [HIGH] sources beat 10 [low] ones
- **Check code-to-text ratios**: [code-heavy 40%] means more code examples

## Example: Researching "Rust Async"

```
1. answer("Rust async runtime comparison")
   → Gets cited overview with 5 sources

2. deep_research("Rust async runtime comparison")
   → Gets 8 sources with quality scores and citations

3. fetch_bulk([url1, url2, url3])  # Top 3 [HIGH] sources
   → Reads them in parallel

4. search_with_citations("tokio vs async-std 2025")
   → Finds recent comparisons with citation IDs

5. fetch_page(new_url, stealth=True)
   → If any are blocked
```
"""


@mcp.tool()
async def answer(
    query: str,
    engine: str = "duckduckgo_lite",
    max_sources: int = 5,
    max_tokens: int = 8000,
) -> str:
    from .tools import tool_answer
    return await tool_answer(query, engine, max_sources, max_tokens)


@mcp.tool()
async def web_search(
    query: str,
    engine: str = "duckduckgo_lite",
    max_results: int = 10,
) -> str:
    from .tools import tool_web_search
    return await tool_web_search(query, engine, max_results)


@mcp.tool()
async def search_with_citations(
    query: str,
    engine: str = "duckduckgo_lite",
    max_results: int = 10,
) -> str:
    from .tools import tool_search_with_citations
    return await tool_search_with_citations(query, engine, max_results)


@mcp.tool()
async def fetch_page(url: str, stealth: bool = False, max_tokens: int = 6000) -> str:
    from .tools import tool_fetch_page
    return await tool_fetch_page(url, stealth, max_tokens)


@mcp.tool()
async def fetch_bulk(
    urls: list[str],
    stealth: bool = False,
    max_concurrent: int = 5,
    max_tokens: int = 3000,
) -> str:
    from .tools import tool_fetch_bulk
    return await tool_fetch_bulk(urls, stealth, max_concurrent, max_tokens)


@mcp.tool()
async def deep_research(
    query: str,
    engine: str = "duckduckgo_lite",
    max_sources: int = 8,
    follow_links: bool = False,
    expand_queries: bool = True,
    max_tokens_per_source: int = 2500,
    max_total_tokens: int = 20000,
    summarize: bool = False,
) -> str:
    from .tools import tool_deep_research
    return await tool_deep_research(
        query, engine, max_sources, follow_links, expand_queries,
        max_tokens_per_source, max_total_tokens, summarize,
    )


@mcp.tool()
async def stealthy_fetch(url: str, max_tokens: int = 6000) -> str:
    from .tools import tool_stealthy_fetch
    return await tool_stealthy_fetch(url, max_tokens)


@mcp.tool()
async def parallel_search(
    queries: list[str],
    engine: str = "duckduckgo_lite",
    max_results: int = 5,
) -> str:
    from .tools import tool_parallel_search
    return await tool_parallel_search(queries, engine, max_results)


def run() -> None:
    import asyncio
    try:
        mcp.run(transport="stdio")
    except Exception:
        asyncio.run(mcp.run_sse())


if __name__ == "__main__":
    run()
