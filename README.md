# maru-search

Universal AI search MCP server. Zero API keys. Scrapes search engines directly and returns cited answers.

[Website](https://claudianus.github.io/maru-search/) · [PyPI](https://pypi.org/project/maru-search/) · [GitHub](https://github.com/claudianus/maru-search)

```bash
pip install maru-search
```

## Connect

**Claude Code:**
```bash
claude mcp add maru-search pip:maru-search
```

**Cursor / VS Code / Windsurf:**
```json
{
  "mcpServers": {
    "maru-search": {
      "command": "python3",
      "args": ["-m", "maru_search.server"]
    }
  }
}
```

## Tools

| Tool | Purpose |
|------|---------|
| `answer` | Direct cited answer to any question (Perplexity-style) |
| `web_search` | Scrape search engines, return ranked results with citation IDs |
| `search_with_citations` | Search with pre-numbered citations for academic writing |
| `fetch_page` | Extract clean content from a single URL |
| `fetch_bulk` | Fetch multiple URLs in parallel |
| `deep_research` | Auto-expand query, crawl top results, synthesize with citations |
| `stealthy_fetch` | Full anti-bot bypass for protected sites |
| `parallel_search` | Run multiple searches simultaneously |

**Quick decision tree:**
- Need a quick answer? → `answer`
- Need sources? → `web_search` or `search_with_citations`
- Have URLs? → `fetch_page` or `fetch_bulk`
- Blocked? → `fetch_page` with `stealth=True`, then `stealthy_fetch`
- Deep dive? → `deep_research`

## What makes it different

- **100% free** — No OpenAI, no Google API, no Bing API. Only direct scraping.
- **Citations** — Every result gets a `[1]`, `[2]` ID. LLMs can cite sources accurately.
- **Multi-engine** — `SearchEngineRegistry` makes adding new scrapers trivial.
- **BM25 ranking** — Local relevance scoring + authority/freshness metadata.
- **Code-aware** — Detects 21 languages, extracts API signatures, measures code-to-text ratio.

## Architecture

```
src/maru_search/
├── server.py              # MCP server (8 tools, 3 prompts)
├── config.py              # Runtime config via env vars
├── tools.py               # Tool implementations + registry
├── engines/
│   ├── registry.py        # SearchEngineRegistry (factory)
│   ├── base.py            # SearchEngine ABC
│   └── duckduckgo.py      # DuckDuckGo scraper
├── research/
│   ├── deep.py            # Deep research + answer synthesis
│   ├── ranker.py          # BM25 + metadata ranking
│   └── expander.py        # Query expansion
├── extraction/
│   ├── code.py            # 21-language detection
│   └── content.py         # Token-aware truncation
└── utils/
    ├── url.py             # URL normalize / filter / dedupe
    └── retry.py           # Exponential backoff
```

## Configuration

Environment variables (all optional):

| Variable | Default | Description |
|----------|---------|-------------|
| `MARU_SEARCH_ENGINE` | `duckduckgo_lite` | Default search engine |
| `MARU_SEARCH_MAX_RESULTS` | `10` | Max results per query |
| `MARU_SEARCH_MAX_CONCURRENT` | `5` | Parallel fetch limit |
| `MARU_SEARCH_MAX_TOKENS_SOURCE` | `2500` | Token budget per source |
| `MARU_SEARCH_MAX_TOKENS_TOTAL` | `20000` | Total output token budget |
| `MARU_SEARCH_TIMEOUT` | `30.0` | Fetch timeout (seconds) |
| `MARU_SEARCH_RETRIES` | `3` | Retry attempts |

## Testing

```bash
pytest tests/ -v
```

124 tests, all passing.

## Dependencies

- [Scrapling](https://github.com/D4Vinci/Scrapling) — browser/HTTP fetching
- [trafilatura](https://trafilatura.readthedocs.io/) — content extraction
- [htmldate](https://htmldate.readthedocs.io/) — publication dates
- [rank-bm25](https://github.com/dorianbrown/rank_bm25) — local relevance scoring
- [MCP SDK](https://github.com/modelcontextprotocol/python-sdk) — MCP protocol

## License

MIT
