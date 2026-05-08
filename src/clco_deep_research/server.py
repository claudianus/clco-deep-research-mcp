from __future__ import annotations

import logging
import sys

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("clco-deep-research")

_logger = logging.getLogger("clco_deep_research")
_logger.setLevel(logging.INFO)

_stderr_handler = logging.StreamHandler(sys.stderr)
_stderr_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
)
_logger.addHandler(_stderr_handler)
_logger.propagate = False


# ═══════════════════════════════════════════════════════════════
# MCP Prompts — Tool Selection Guidance for AI Agents
# ═══════════════════════════════════════════════════════════════

@mcp.prompt()
def tool_selection_guide() -> str:
    """Comprehensive guide for choosing the right research tool."""
    return """# clco-deep-research Tool Selection Guide

## Quick Decision Tree

```
What do you need?
├── Find information on a topic?
│   ├── Single angle → web_search
│   └── Multiple angles → parallel_search
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

### web_search
**When to use**: You need to find sources on a single topic.
**Example**: "Python asyncio best practices"
**Returns**: Ranked results with [AUTHORITY] badges and content type hints.
**NOT for**: Reading known URLs.

### parallel_search
**When to use**: You need multiple perspectives simultaneously.
**Example**: ["Python vs Go performance", "Python concurrency tutorial", "Python async pitfalls"]
**Returns**: Separate result sets for each query, merged output.
**NOT for**: Single simple queries (use web_search instead).

### fetch_page
**When to use**: You have a specific URL to read.
**Example**: "https://docs.python.org/3/library/asyncio.html"
**Returns**: Clean extracted content with quality signals.
**Anti-bot fallback**: If blocked, retry with stealth=True.

### fetch_bulk
**When to use**: You have 2-10 URLs from search results.
**Example**: ["url1", "url2", "url3"] from web_search results
**Returns**: All pages in parallel with quality badges.
**NOT for**: Single URLs (use fetch_page instead).

### deep_research
**When to use**: You need comprehensive research on an unfamiliar topic.
**Example**: "Explain Kubernetes networking to me"
**Returns**: Synthesized findings from multiple sources with quality scoring.
**Parameters**:
- max_sources: How many pages to crawl (default 8)
- summarize=True: Enable if output is too large
- follow_links=True: For deeper coverage (slower)

### stealthy_fetch
**When to use**: fetch_page failed even with stealth=True.
**Example**: Cloudflare-protected sites
**Returns**: Same as fetch_page but with full browser automation.
**Warning**: ~3-5x slower. Use as last resort.

## Performance Ranking
1. **Fastest**: web_search, fetch_page
2. **Medium**: parallel_search, fetch_bulk
3. **Slow**: deep_research
4. **Slowest**: stealthy_fetch

## Common Mistakes
- ❌ Using stealthy_fetch for every URL
- ❌ Using deep_research for single-page reads
- ❌ Not checking quality badges ([HIGH], [BLOCKED])
- ❌ Ignoring follow-up links in results
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
- Use web_search to find mirrors or cached versions

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

1. Start with `deep_research(query)` for broad exploration
   - Let it auto-expand queries
   - Review quality badges ([HIGH] = prioritize)
   - Note promising URLs

2. OR use `parallel_search` for targeted angles:
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
**Goal**: Combine findings

1. Review all fetched content
2. Use follow-up links from results for additional sources
3. Cross-reference information across sources

## Token Management Tips

- **Default budgets are generous** (fetch_page: 6000 tokens)
- **Use summarize=True** in deep_research if output exceeds context window
- **Quality over quantity**: 3 [HIGH] sources beat 10 [low] ones
- **Check code-to-text ratios**: [code-heavy 40%] means more code examples

## Example: Researching "Rust Async"

```
1. deep_research("Rust async runtime comparison")
   → Gets 8 sources with quality scores

2. fetch_bulk([url1, url2, url3])  # Top 3 [HIGH] sources
   → Reads them in parallel

3. web_search("tokio vs async-std 2025")
   → Finds recent comparisons

4. fetch_page(new_url, stealth=True)
   → If any are blocked
```
"""


@mcp.tool()
async def web_search(
    query: str,
    engine: str = "duckduckgo_lite",
    max_results: int = 10,
) -> str:
    from .tools import tool_web_search

    return await tool_web_search(query, engine, max_results)


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
