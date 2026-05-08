# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2026-05-08

### Added
- **Smart Token Management**: Dynamic token allocation based on source quality
  - `_allocate_tokens()`: High-quality sources get 100% budget, medium 70%, low 40%
  - `max_total_tokens` parameter (default: 20000) for total output budget control
  - `summarize=True` enables extractive summarization for over-budget scenarios
  - `_extractive_summarize()`: Preserves headings and key paragraphs
- **Enhanced Korean Support**:
  - Korean query auto-detection (한글 characters + keywords)
  - Korean-specific query templates: korean_community, korean_docs
  - Korean authority domains: velog.io, tistory.com, naver.com, brunch.co.kr, okky.kr
  - Korean content type classification for developer blogs
- **AI Agent Tool Guidance**:
  - `TOOL_GUIDANCE`: Comprehensive tool selection guide with decision tree
  - 3 MCP prompts: `tool_selection_guide`, `anti_bot_strategy`, `research_workflow`
  - Enhanced tool descriptions with BEST FOR / NOT FOR / TRY FIRST / LAST RESORT labels
  - Performance ranking and common mistakes documentation
- **Increased Token Defaults**:
  - fetch_page: 3000 → 6000
  - fetch_bulk: 1500 → 3000
  - stealthy_fetch: 3000 → 6000
  - deep_research per-source: 1500 → 2500

### Changed
- Tool registry descriptions now include usage scenarios and decision criteria
- README updated with Tool Selection Guide, MCP Prompts section, and v0.4.0 features
- GitHub Pages updated with v0.4.0 stats and features
- Test suite expanded: 68 → 113 tests

## [0.3.0] - 2026-05-08

### Added
- Query expansion: 3-5 orthogonal subqueries for broader coverage
- Relevance scoring: Authority + content type + freshness + position
- Structured exception hierarchy: 7 exception classes with retry hints
- Fault-tolerant CSS selectors with multiple fallbacks
- Package detection: Extract package/library references from code
- URL normalization and filtering utilities
- Exponential backoff retry mechanism
- 21 language detection (up from 16)
- New test suite: 68 tests (up from 35)
- GitHub Pages website

### Changed
- Improved deep research pipeline with multi-pass crawling
- Enhanced error handling with engine fallback
- Better content extraction with trafilatura
- Updated README with v0.3.0 features

## [0.2.2] - 2025-05-07

### Added
- Initial test suite (35 tests)
- Code-aware analysis module
- DuckDuckGo SERP scraping
- Basic deep research pipeline

## [0.2.0] - 2025-05-07

### Added
- Initial release
- 6 MCP tools: web_search, fetch_page, fetch_bulk, deep_research, stealthy_fetch, parallel_search
- Scrapling integration
- trafilatura content extraction
