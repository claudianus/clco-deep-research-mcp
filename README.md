<h1 align="center"><code>maru-deep-pro-search</code></h1>

<p align="center">
  <strong>Force your AI agent to research before it codes.</strong><br>
  Zero API keys · Direct scraping · Citation-native · Semantic hybrid ranking · Smart fallback
</p>

<p align="center">
  <a href="./README.ko.md">🇰🇷 한국어</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/maru-deep-pro-search/"><img src="https://img.shields.io/pypi/v/maru-deep-pro-search?style=flat-square&color=blue" alt="PyPI"></a>
  <a href="https://github.com/claudianus/maru-deep-pro-search/actions"><img src="https://img.shields.io/github/actions/workflow/status/claudianus/maru-deep-pro-search/publish.yml?style=flat-square&label=CI" alt="CI"></a>
  <a href="https://github.com/claudianus/maru-deep-pro-search/blob/main/tests/"><img src="https://img.shields.io/badge/tests-193%20passing-brightgreen?style=flat-square" alt="Tests"></a>
  <a href="https://pypi.org/project/maru-deep-pro-search/"><img src="https://img.shields.io/pypi/pyversions/maru-deep-pro-search?style=flat-square" alt="Python"></a>
  <a href="https://github.com/claudianus/maru-deep-pro-search/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-brightgreen?style=flat-square" alt="License"></a>
</p>

<p align="center">
  <a href="https://claudianus.github.io/maru-deep-pro-search/">🌐 Website</a> ·
  <a href="https://pypi.org/project/maru-deep-pro-search/">📦 PyPI</a> ·
  <a href="https://github.com/claudianus/maru-deep-pro-search">💻 GitHub</a>
</p>

---

## One-liner Install

**macOS / Linux:**
```bash
curl -sSL https://raw.githubusercontent.com/claudianus/maru-deep-pro-search/main/scripts/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/claudianus/maru-deep-pro-search/main/scripts/install.ps1 | iex
```

Or with pip:
```bash
pip install maru-deep-pro-search[semantic] && maru-deep-pro-search setup
```

The setup wizard auto-detects your AI agent (Claude Code, Cursor, Kimi, Windsurf, etc.), backs up existing configs, injects MCP settings, and enforces research-first rules. The `[semantic]` extra installs `sentence-transformers>=3.0.0` for dense vector ranking.

---

## What it does

Your AI coding agent has a critical flaw: it answers from stale training data. `maru-deep-pro-search` fixes this by giving your agent live web search superpowers — and **forcing it to use them first**.

| Capability | How |
|-----------|-----|
| **Search** | Scrapes 7 engines directly via async HTTP. No API keys. |
| **Rank** | BM25 + dense semantic similarity + authority/freshness/code-density scoring |
| **Research** | 7-phase deep research pipeline with auto query expansion, smart fetch, and gap detection |
| **Cite** | Every result gets `[1]`, `[2]` IDs — native citation architecture |
| **Enforce** | Setup CLI injects mandatory research-first rules into your agent |
| **Persist** | Harness platform stores project knowledge in SQLite with optional semantic embeddings |

**Core principle:** 100% free, forever. No OpenAI, no Anthropic, no Google Search API, no SerpAPI, no Bing API. Only direct scraping and local computation.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         MCP Client Layer                              │
│                (Claude Code, Cursor, Kimi, Windsurf)                  │
└───────────────────────────────┬───────────────────────────────────────┘
                                │ JSON-RPC 2.0 / stdio
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      maru-deep-pro-search                             │
│                          MCP Server                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │
│  │ 4 Prompts    │  │ 8 Tools      │  │ TOOL_GUIDANCE            │   │
│  │ (always_     │  │              │  │ (context-level rules)    │   │
│  │  research_   │  │              │  │                          │   │
│  │  first, ...) │  │              │  │                          │   │
│  └──────────────┘  └──────┬───────┘  └──────────────────────────┘   │
│                           │                                          │
└───────────────────────────┼──────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       Research Pipeline                               │
│                                                                       │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────────┐    │
│  │ Query       │──▶│ 7 Engines   │──▶│ Result Merge &          │    │
│  │ Expander    │   │ (async)     │   │ Fuzzy Deduplication     │    │
│  │ (templates  │   │ Registry    │   │ (Jaccard + semantic)    │    │
│  │ + synonyms) │   │ pattern)    │   │                         │    │
│  └─────────────┘   └─────────────┘   └───────────┬─────────────┘    │
│                                                  │                   │
│  ┌───────────────────────────────────────────────┘                   │
│  ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Hybrid Ranking Engine                                         │   │
│  │  • BM25: k1=1.5, b=0.75 on title + snippet (rank-bm25)        │   │
│  │  • Metadata: authority × freshness × code_density             │   │
│  │  • Semantic: cos_sim(query, text) via multilingual-e5-small   │   │
│  │    (33M params, 384-dim, 100+ languages, MTEB 59.3)           │   │
│  │  • Final: weighted ensemble with engine confidence            │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                             │                                        │
│  ┌──────────────────────────┘                                        │
│  ▼                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Smart Fetch Layer                                             │   │
│  │  • Network probe (DuckDuckGo RTT) → adaptive timeout          │   │
│  │  • Domain history filter (slow>5s or fail>80% → skip)         │   │
│  │  • Priority queue: authority domains first                    │   │
│  │  • Error-type-aware strategy:                                 │   │
│  │    DNS/Network → skip | SSL → stealth retry | 403→stealth    │   │
│  │  • Scrapling session reuse (AsyncDynamicSession pool)         │   │
│  │    disable_resources=True, block_ads=True, timeout in ms      │   │
│  │  • Early abort: stop when 3 HIGH quality results obtained     │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                             │                                        │
│  ┌──────────────────────────┘                                        │
│  ▼                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Content Extraction Pipeline                                   │   │
│  │  • trafilatura: main text + metadata extraction               │   │
│  │  • htmldate: publish date detection                           │   │
│  │  • code.py: 21-language syntax detection, API extraction      │   │
│  │  • sanitize.py: zero-width char removal, chat token           │   │
│  │    neutralization, suspicious pattern flagging                │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                             │                                        │
│  ┌──────────────────────────┘                                        │
│  ▼                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Synthesis & Citation                                          │   │
│  │  • Rule-based synthesis (zero LLM in server)                  │   │
│  │  • Native [1], [2], [3] citation IDs                          │   │
│  │  • Gap detection for incomplete research                      │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

The server contains **zero generative LLMs**. Synthesis is rule-based; your agent's LLM handles reasoning. Optional semantic scoring uses an embedding model (bi-encoder only, no generation).

---

## 8 Tools

| Tool | Purpose | When to use |
|------|---------|-------------|
| `answer` | Quick answer with inline citations | Simple factual questions |
| `web_search` | Scrape + rank + return cited results | Need ranked sources |
| `search_with_citations` | Pre-numbered sources for academic writing | Documentation, papers |
| `fetch_page` | Extract clean content from a single URL | Known source deep-dive |
| `fetch_bulk` | Parallel fetch with deduplication | Multiple known URLs |
| `deep_research` | Full 7-phase pipeline with gap detection | Complex technical questions |
| `stealthy_fetch` | Anti-bot bypass for protected sites | Blocked by Cloudflare/etc |
| `parallel_search` | Run multiple searches simultaneously | Comparative analysis |

**Decision tree:**
- Quick answer? → `answer`
- Need sources? → `web_search` or `search_with_citations`
- Deep dive? → `deep_research`
- Blocked? → `stealthy_fetch`

---

## Technical Deep Dives

### Query Expansion Engine

Before hitting any search engine, the original query is expanded using a template-based system:

- **Templates**: `"{query} tutorial"`, `"{query} best practices"`, `"{query} documentation"`, `"{query} github"`, `"{query} vs alternative"`
- **Synonym injection**: Technical terms get expanded with common aliases (e.g., "docker compose" → "docker-compose")
- **Language awareness**: Korean queries get Korean-specific templates (e.g., `"{query} 사용법"`, `"{query} 예제"`)
- **Output**: 5–7 expanded queries per original, executed in parallel across all engines

### Multi-Engine Search Layer

Seven search engines are supported, all via direct scraping:

| Engine | Method | Failover |
|--------|--------|----------|
| DuckDuckGo (lite) | HTML scrape | Primary |
| DuckDuckGo (html) | HTML scrape | Fallback |
| SearXNG | JSON API | 6-instance round-robin |
| Bing | HTML scrape | — |
| Google | HTML scrape + CAPTCHA detection | — |
| Naver | Korean-specific HTML scrape | — |
| Qwant | European privacy-focused | — |
| Startpage | Google via privacy proxy | — |

**Registry pattern**: `SearchEngineRegistry` uses a factory with `_instances` dict for singleton reuse. All engines share the same `AsyncDynamicSession` instance, eliminating ~2s browser startup overhead per fetch.

**Parallel execution**: `asyncio.gather()` across all configured engines. Results are merged and deduplicated before ranking.

### Hybrid Ranking Algorithm

The ranking engine combines four signals into a weighted ensemble:

```
final_score = bm25_score      × 0.35
            + authority_score × 0.20
            + freshness_score × 0.15
            + code_density    × 0.10
            + semantic_score  × 0.20   (if sentence-transformers installed)
```

**BM25** (`rank-bm25`, k1=1.5, b=0.75): Computed over title + snippet corpus. BM25 is a probabilistic retrieval function that scores documents based on term frequency and inverse document frequency, with saturation and length normalization.

**Authority scoring**:
- Domain whitelist bonus: `github.com`, `docs.python.org`, `developer.mozilla.org`, etc. get +0.3
- TLD scoring: `.edu`, `.gov`, `.ac.kr` get +0.2; `.blog`, `.medium` get -0.1
- Path depth penalty: deeper paths (e.g., `/a/b/c/d`) get slightly lower scores

**Freshness scoring** (`htmldate`):
- Extracts publish date from HTML metadata
- Exponential decay: `score = exp(-days_old / 365)`
- Undated pages get neutral score (0.5)

**Code density** (`pygments`):
- Tokenizes content with language-appropriate lexer
- `code_density = code_tokens / total_tokens`
- Technical queries boost pages with high code density

**Semantic scoring** (optional, `sentence-transformers>=3.0.0`):
- Model: `intfloat/multilingual-e5-small` (33M parameters, 384 dimensions, 100+ languages, MIT license, MTEB 59.3)
- Why this model: replaces `all-MiniLM-L6-v2` (EN-only, 2021) with modern multilingual support including Korean
- Cosine similarity between query embedding and page text embedding (first 300 chars)
- Batch processing for efficiency
- **Not a generative LLM**: embedding-only bi-encoder. No factual reasoning, no hallucination risk.
- Cross-encoder was evaluated and removed: marginal gains (<2%) not worth 3× latency increase

**Deduplication**:
- URL-level exact dedup (normalized via `urllib.parse`)
- Fuzzy dedup: Jaccard similarity on title + snippet (threshold 0.72)
- Semantic fallback dedup: cosine similarity >0.95 for near-duplicate detection

### Smart Fetch & Resilience

The fetch layer is designed for production-grade reliability:

**Network probe** (`_probe_network()`):
- Measures DuckDuckGo RTT on every `deep_research` call
- Adjusts `timeout_per_fetch` and `max_sources` based on latency
- Slow network (>5s RTT): reduces concurrency, increases timeouts

**Domain history** (`KnowledgeStore.domain_stats`):
- SQLite table tracking per-domain `avg_duration_ms`, `failure_rate`, `last_updated`
- Slow domains (>5s average) are preemptively skipped
- Unreliable domains (>80% failure rate) are blacklisted
- Updated after every fetch attempt

**Error-type-aware handling**:

| Error | Strategy |
|-------|----------|
| DNS / Network unreachable | Skip domain immediately |
| SSL certificate error | Retry with `AsyncStealthySession` |
| HTTP 403 / 429 | Retry with stealth + reduced concurrency |
| HTTP 404 | Skip |
| Timeout | Retry once with increased timeout (+3s) |
| CAPTCHA (Google only) | Flag and skip |

**Scrapling optimizations**:
- `AsyncDynamicSession` with `disable_resources=True`, `block_ads=True`
- Session reuse via `_get_session()` — single session per engine instance
- `timeout` parameter is in **milliseconds** (converted via `int(timeout * 1000)`)
- Built-in retry: `retries=2`, `retry_delay=1`

**Early abort**:
- `asyncio.as_completed()` with `max_concurrent=5`
- Stops when 3 `HIGH` quality results (trafilatura extraction + content_length > 200) are obtained
- Proper Task cancellation in `finally` block to prevent dangling coroutines

### Content Extraction Pipeline

```
Raw HTML
    │
    ▼
┌─────────────────┐
│ trafilatura     │ → main text, title, metadata
│ (main content)  │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│htmldate│ │ code.py  │
│(date)  │ │(syntax)  │
└────────┘ └──────────┘
    │         │
    ▼         ▼
┌─────────────────┐
│ sanitize.py     │ → safe for LLM injection
│ (defense layer) │
└─────────────────┘
```

**trafilatura**: Extracts main content from HTML, removing navigation, ads, sidebars. Returns clean markdown-like text.

**htmldate**: Heuristic date extraction from HTML metadata, JSON-LD, and content analysis.

**code.py**: 21-language syntax detection using Pygments lexers. Extracts API signatures, function names, and code blocks for code-density scoring.

**sanitize.py**: Prompt injection defense layer:
- Zero-width character removal (`\u200b`, `\u200c`, `\u200d`, `\ufeff`)
- Chat token neutralization: sequences like `Human:`, `Assistant:`, `System:` are replaced with `[REDACTED]`
- Suspicious pattern detection: excessive repetition (>50% of content), base64 blobs (>1KB), unicode homoglyphs
- All sanitization happens **before** LLM context injection

### Semantic Search (Optional)

The optional semantic module adds dense vector similarity without any generative capabilities:

- **Model**: `intfloat/multilingual-e5-small`
  - 33M parameters, 384-dimensional embeddings
  - 100+ languages including Korean, Japanese, Chinese
  - MIT license (commercial use allowed)
  - MTEB score: 59.3 (vs all-MiniLM-L6-v2's 56.3)
- **Architecture**: Bi-encoder only. Query and document are encoded independently, similarity is cosine distance.
- **No Cross-Encoder**: Was evaluated and removed. Cross-encoder added ~800ms latency for <2% relevance improvement. Bi-encoder + BM25 hybrid is sufficient.
- **Lazy loading**: Model loads on first use via `_LazyModels` singleton. CPU-only.
- **Graceful degradation**: If `sentence-transformers` is not installed, all semantic branches silently skip with zero runtime errors.

Install: `pip install maru-deep-pro-search[semantic]`

### Harness Platform

Project-level knowledge persistence for long-running research workflows:

**KnowledgeStore** (SQLite):
- `pages`: extracted content with full-text search (FTS5)
- `domain_stats`: per-domain performance tracking
- `semantic_embeddings`: optional vector storage for similarity search
- `projects`: project metadata and configuration

**WorkflowEngine** (7-phase generator):
1. **Probe**: Network health check
2. **Expand**: Query expansion
3. **Search**: Multi-engine parallel search
4. **Rank**: Hybrid ranking + deduplication
5. **Fetch**: Smart fetch with domain filtering
6. **Extract**: Content extraction + sanitization
7. **Synthesize**: Rule-based answer + citation + gap detection

**CLI commands**:
```bash
maru-deep-pro-search init          # Initialize .maru/ in current directory
maru-deep-pro-search setup         # Configure AI agent integration
```

### Citation Architecture

Native citation IDs are assigned **before** synthesis, ensuring every claim can be traced:

1. Search results are collected from all engines
2. URL deduplication + fuzzy deduplication
3. Hybrid ranking produces final ordering
4. Sequential IDs `[1]`, `[2]`, `[3]` are assigned based on final rank
5. Synthesis references these stable IDs
6. LLM receives pre-numbered sources, preventing hallucinated citations

The `search_with_citations` tool returns sources in academic format with URLs, titles, and publish dates.

---

## Performance Characteristics

| Metric | Target | Implementation |
|--------|--------|----------------|
| Cache hit (KnowledgeStore) | <100ms | SQLite FTS5 + indexed domain_stats |
| Full `deep_research` | <10s | 7 engines, 5 concurrent, early abort at 3 HIGH results |
| Scrapling session startup | ~0ms (amortized) | Single session reused per engine instance |
| Semantic model load | ~2s (first call only) | Lazy init, CPU-only |
| Memory footprint | ~150MB base, +120MB with semantic | No GPU required |

---

## Configuration Reference

All environment variables are optional. Runtime config is loaded via `pydantic-settings` with env prefix `MARU_SEARCH_`.

| Variable | Default | Description |
|----------|---------|-------------|
| `MARU_SEARCH_ENGINE` | `duckduckgo_lite` | Default search engine |
| `MARU_SEARCH_MAX_RESULTS` | `10` | Results per query per engine |
| `MARU_SEARCH_MAX_CONCURRENT` | `5` | Parallel fetch limit |
| `MARU_SEARCH_MAX_TOKENS_SOURCE` | `2500` | Token budget per extracted source |
| `MARU_SEARCH_MAX_TOKENS_TOTAL` | `20000` | Total output token budget |
| `MARU_SEARCH_TIMEOUT` | `30.0` | Fetch timeout (seconds) |
| `MARU_SEARCH_RETRIES` | `3` | Retry attempts for transient failures |
| `MARU_SEARCH_STEALTH_TIMEOUT` | `15.0` | Stealth session timeout (seconds) |
| `MARU_SEARCH_MIN_QUALITY_RESULTS` | `3` | Early abort threshold for HIGH quality results |

---

## Before & After

| | Before | After |
|---|---|---|
| **Agent answers** | From stale 2023 training data | From live web search with freshness scoring |
| **Sources** | None, hallucinated | `[1]`, `[2]` with real URLs and publish dates |
| **Setup** | Manual MCP config per agent | One-liner auto-detects all agents |
| **Cost** | $5–50/mo API fees | **$0 forever** |
| **Ranking** | Raw engine ordering | BM25 + semantic + metadata hybrid |
| **Resilience** | Single point of failure | 7-engine failover + smart fallback |
| **Persistence** | Stateless | Project-level SQLite knowledge store |

---

## Testing

```bash
pytest tests/ -v
```

193 tests, all passing. Coverage includes unit tests for all engines, ranking algorithms, content extraction, sanitization, harness persistence, and integration tests for the full research pipeline.

---

## Contributing

PRs welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md) for coding style and PR guidelines.

See [CHANGELOG.md](./CHANGELOG.md) for release history.

---

## License

MIT © [claudianus](https://github.com/claudianus)
