<p align="center">
  <a href="https://claudianus.github.io/clco-deep-research-mcp/">🌐 Website</a> •
  <a href="https://pypi.org/project/clco-deep-research-mcp/">📦 PyPI</a> •
  <a href="https://github.com/claudianus/clco-deep-research-mcp">⭐ GitHub</a>
</p>

<p align="center">
  <img src="https://img.shields.io/pypi/v/clco-deep-research-mcp?color=blue&label=PyPI" alt="PyPI">
  <img src="https://img.shields.io/pypi/pyversions/clco-deep-research-mcp?color=green" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-purple" alt="License">
  <img src="https://img.shields.io/badge/MCP-native-blue" alt="MCP Native">
  <img src="https://img.shields.io/badge/engines-4-orange" alt="4 Search Engines">
  <img src="https://img.shields.io/badge/cost-free-brightgreen" alt="Free">
</p>

# clco-deep-research-mcp

**The free, coding-agent-optimized deep research MCP that replaces Claude Code's built-in web_search.**

> Claude Code의 `web_search` 툴이 프록시 환경에서 작동하지 않나요? 이 MCP가 완전히 대체합니다. 4개 검색엔진을 직접 스크래핑하고, trafilatura로 본문을 추출하며, 코드 언어/API 시그니처/최신성을 자동 분석합니다. **API 키 불필요, 완전 묣이.**

## What's New in v0.3.0

- **Query Expansion**: Automatically generates 3-5 orthogonal subqueries for broader coverage
- **Relevance Scoring**: Multi-factor scoring (authority + content type + freshness + position)
- **Enhanced Error Handling**: Structured exceptions with retry hints and engine fallback
- **Improved Selectors**: Fault-tolerant CSS selectors with multiple fallbacks
- **Package Detection**: Automatically extracts package/library references from code
- **Better Deep Research**: Multi-pass crawling with link following and content synthesis

## Quick Start

```bash
# Install globally (recommended)
pip install clco-deep-research-mcp

# Run directly
python3 -m clco_deep_research.server
```

**Claude Code** (`~/.claude.json`):
```json
{
  "mcpServers": {
    "clco-deep-research": {
      "command": "python3",
      "args": ["-m", "clco_deep_research.server"]
    }
  }
}
```

**Cursor** (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "clco-deep-research": {
      "command": "python3",
      "args": ["-m", "clco_deep_research.server"]
    }
  }
}
```

**VS Code** (`.vscode/mcp.json`):
```json
{
  "servers": {
    "clco-deep-research": {
      "type": "stdio",
      "command": "python3",
      "args": ["-m", "clco_deep_research.server"]
    }
  }
}
```

**Windsurf** (`.windsurf/mcp_config.json`):
```json
{
  "mcpServers": {
    "clco-deep-research": {
      "command": "python3",
      "args": ["-m", "clco_deep_research.server"]
    }
  }
}
```

## Tools (6)

| Tool | Description | Key Feature |
|------|-------------|-------------|
| `web_search` | Scrape search engines directly | Content type hints + authority badges |
| `fetch_page` | Extract clean content from any URL | trafilatura + code-aware metadata |
| `fetch_bulk` | Parallel multi-URL fetch | Quality signals for LLM prioritization |
| `deep_research` | Full pipeline with query expansion | Multi-angle research + synthesis |
| `stealthy_fetch` | Full anti-bot bypass | Cloudflare Turnstile, DataDome |
| `parallel_search` | Multiple queries in parallel | Multi-engine scatter-gather |

## Deep Research Pipeline

```
Query
  ↓
[Query Expansion] → 3-5 orthogonal subqueries
  ↓
[Parallel Search] → Execute across engines
  ↓
[Deduplication] → URL normalization + content hashing
  ↓
[Relevance Scoring] → Authority + type + freshness + position
  ↓
[Multi-Pass Crawling] → BFS with depth limit
  ↓
[Content Extraction] → trafilatura + code-aware + structured data
  ↓
[Synthesis] → Aggregate by topic with confidence scores
  ↓
[Formatting] → Markdown with quality badges + relevance scores
```

## Architecture

```
src/clco_deep_research/
├── server.py              # MCP server (stdio)
├── exceptions.py          # Structured error hierarchy
├── tools.py               # 6 MCP tools
├── engines/
│   ├── base.py            # Abstract engine interface
│   └── duckduckgo.py      # DuckDuckGo (improved selectors)
├── extraction/
│   ├── content.py         # trafilatura wrapper
│   └── code.py            # Code-aware analysis (21 languages)
├── research/
│   ├── deep.py            # Deep research pipeline
│   └── expander.py        # Query expansion
└── utils/
    ├── retry.py           # Exponential backoff
    └── url.py             # URL normalization/filtering
```

## Code-Aware Metadata

Every fetched page is analyzed for coding-agent relevance:

```markdown
### [1] Async Context Managers in Python [HIGH] [API-REF] [python] [code-heavy 32%] [293d ago] [AUTHORITY]
URL: https://dev.to/...
_relevance: 5.3_
_APIs: async def __aenter__(self):; async def __aexit__(...):_
_Packages: aiohttp (python), fastapi (python)_
```

| Signal | What It Tells the LLM |
|--------|----------------------|
| `[HIGH]` | trafilatura quality score — prioritize this source |
| `[API-REF]` | Content type classification |
| `[python]` | Detected languages from code blocks |
| `[code-heavy 32%]` | Code-to-text ratio — skim vs deep-read |
| `[293d ago]` | Freshness — warn if >1yr stale |
| `[AUTHORITY]` | From known high-quality domain |
| `APIs:` | Function/class signatures for quick scanning |
| `Packages:` | Package/library references with language |

## Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| [Scrapling](https://github.com/D4Vinci/Scrapling) | ≥0.2.0 | Browser/HTTP fetching, anti-bot |
| [trafilatura](https://trafilatura.readthedocs.io/) | ≥2.0.0 | Main content extraction (SOTA) |
| [htmldate](https://htmldate.readthedocs.io/) | ≥1.9.4 | Publication date extraction |
| [Pygments](https://pygments.org/) | ≥2.20.0 | Syntax highlighting (reference) |
| [MCP SDK](https://github.com/modelcontextprotocol/python-sdk) | ≥1.0.0 | Model Context Protocol server |

## Error Handling

Structured exceptions help the LLM decide what to do:

```python
NetworkError("timeout")        # retryable=True, auto-retry with backoff
BlockedError("captcha")        # retryable=True, fallback to duckduckgo_lite
ParseError("selectors broken") # retryable=True, fallback to duckduckgo_lite
NoResultsError("empty")        # retryable=False, suggest query refinement
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_query_expansion.py -v
```

**Current coverage**: 68 tests, all passing.

## License

MIT — use it, fork it, ship it. Built for the coding agent era.

---

<p align="center">
  <sub>Made for <a href="https://github.com/claudianus/clco-helper">clco-helper</a> — the Claude Code power tool</sub>
</p>
