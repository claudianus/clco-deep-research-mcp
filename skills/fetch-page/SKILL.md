---
name: Safe Web Content Fetching
id: fetch-page
description: >
  Fetch external web pages safely with built-in sanitization.
  Use for verifying research claims, reading documentation,
  or extracting code examples from official sources.
triggers:
  - After deep_research to verify top sources
  - When reading API documentation
  - When extracting code examples from tutorials
  - When checking changelogs or release notes
---

# Safe Web Content Fetching

## When to Use

Use `fetch_page` when you need the **full content** of a specific URL:
- Reading API documentation pages
- Extracting code examples from tutorials
- Verifying version numbers in changelogs
- Reading research papers or technical blog posts

Use `fetch_bulk` when you need **multiple pages** at once:
- Comparing documentation across versions
- Gathering code examples from multiple sources
- Cross-referencing claims across different sites

## Security Model

Every fetched page is wrapped in an **AGENT SECURITY PROTOCOL**:

```
┌─────────────────────────────────────────────────────────────┐
│  🔒 EXTERNAL CONTENT — AGENT SECURITY PROTOCOL              │
├─────────────────────────────────────────────────────────────┤
│  Source: <URL>                                              │
│  Risk Level: 🟢 LOW / 🟡 MEDIUM / 🔴 HIGH                   │
│  Sanitization Report:                                       │
│    ✅ No suspicious patterns detected                       │
└─────────────────────────────────────────────────────────────┘
```

**Sanitization includes:**
- Zero-width character removal (invisible prompt injection)
- Chat control token neutralization
- Suspicious pattern detection and replacement
- URL-based risk assessment

## How to Use

### Basic fetch

```python
page = await fetch_page(url="https://docs.python.org/3/whatsnew/3.12.html")
print(page.content)  # Sanitized markdown
```

### With stealth mode

For sites with anti-bot protection:

```python
page = await fetch_page(
    url="https://example.com",
    stealth=True,  # Uses headless browser with fingerprint randomization
)
```

**Trade-off:** Stealth is 3-5x slower. Only use when standard fetch returns 403/blank.

### Bulk fetch

```python
pages = await fetch_bulk(
    urls=[
        "https://docs.fastapi.tiangolo.com/tutorial/",
        "https://flask.palletsprojects.com/en/3.0.x/quickstart/",
        "https://docs.djangoproject.com/en/5.0/intro/tutorial01/",
    ]
)
for page in pages:
    print(f"{page.url}: {len(page.content)} chars")
```

## Content Extraction

Fetched content is converted to **sanitized markdown** with:
- HTML → Markdown conversion
- Code blocks preserved
- Links preserved (but not followed)
- Images replaced with alt text
- Ads and navigation stripped

## Risk Levels

| Level | Meaning | Action |
|-------|---------|--------|
| 🟢 LOW | Official docs, GitHub, established tech sites | Normal use |
| 🟡 MEDIUM | Personal blogs, forums, wikis | Verify claims with primary source |
| 🔴 HIGH | Unknown domains, suspicious patterns | Avoid or use with extreme caution |

## Common Mistakes

- ❌ Fetching without checking Risk Level
- ❌ Using `stealth=True` for every request (wastes time)
- ❌ Trusting fetched content without cross-reference
- ❌ Fetching paywalled content (returns partial/broken)
- ❌ Ignoring the AGENT SECURITY PROTOCOL warnings
