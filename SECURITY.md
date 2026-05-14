# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.11.x  | ✅ Active development |
| < 0.11.0 | ❌ No longer supported |

## Reporting a Vulnerability

If you discover a security vulnerability in `maru-deep-pro-search`, please report it responsibly:

1. **Do NOT open a public issue.**
2. Open a [GitHub Security Advisory](https://github.com/claudianus/maru-deep-pro-search/security/advisories/new) or email **security@maru.dev** with:
   - A clear description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if any)

You can expect:
- An acknowledgment within 48 hours
- A detailed response within 7 days
- Credit in the changelog upon resolution (unless you prefer anonymity)

## Security Features

This project implements multiple defense layers:

### Research Enforcement (3-Layer Architecture)

> **This is not prompt injection.** LLMs can ignore text. These are technical gates.

- **Layer 1 — Server-side gate**: `SessionEnforcer` tracks every MCP session. Tools like `fetch_page`, `web_search`, `answer` return a hard error if `deep_research` hasn't been called first. Research expires after 30 minutes.
- **Layer 2 — Client-side hooks**: Physical blocking before the agent can act:
  - **Claude Code**: `PreToolUse` hook (exit code 2) blocks `Write`/`Edit`
  - **Aider**: `lint-cmd` gate script fails if research is incomplete
  - **Cursor**: Custom `/research` and `/verify` slash commands + `.cursorrules`
  - **Hermes**: `pre_tool_call` plugin hook blocks un-researched tools; `post_tool_call` hook audits; `on_session_start` resets gate
- **Layer 3 — Tool dependency** (roadmap): Future `generate_code()` will require a `research_id` parameter matching a completed research session.

### Input Defense

- **72 prompt injection signatures** covering 10+ languages
- **MCP-specific attack detection**: tool poisoning, rug pulls, shadowing, MPMA
- **Content sanitization**: zero-width character stripping, token neutralization
- **Audit logging**: behavioral anomaly detection for tool invocations
- **Docker sandbox**: isolated execution environment

## Known Limitations

- Search results depend on the security posture of scraped websites
- Semantic embedding models run locally (CPU-only) — no external API calls
- Audit logs are stored locally in SQLite; rotate `.maru/audit.db` periodically
