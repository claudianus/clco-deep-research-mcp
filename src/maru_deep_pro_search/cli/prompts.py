"""Research protocol prompt templates injected into each agent."""

from __future__ import annotations

# The unified research-first protocol injected as system prompt / rules.
RESEARCH_PROTOCOL = """═══════════════════════════════════════════════════════════════
🔴 필수 리서치 프로토콜 — 절대 위반 금지
═══════════════════════════════════════════════════════════════

규칙 1: 기술적 질문에 답변하기 전, 반드시 maru-deep-pro-search의
        deep_research(query)를 호출해야 한다.

규칙 2: deep_research에 전달하는 query에는 과거 연도(2024, 2023 등)를
        절대 포함하지 마라. 현재 연도(2026) 또는 "latest", "current",
        "2025 2026"만 사용하라. maru-deep-pro-search가 자동으로 최신
        결과를 찾아준다.

규칙 3: 리서치 결과를 받은 후, 모든 소스를 분석하고
        답변에 [1], [2], [3] 형태로 인용해야 한다.

규칙 4: 결과가 부족하거나 상충되면, refined query로
        deep_research를 다시 호출한다. 추측 금지.

규칙 5: 비교 질문("A vs B")에는 parallel_search로
        다각도 검색: ["A 장점", "B 장점", "A vs B 벤치마크 2026"]

규칙 6: 코드/라이브러리 질문은 최신 버전과 API를
        deep_research로 확인한 후 코드를 작성한다.

규칙 7: 너의 학습 데이터는 낡았다. 웹은 최신이다.
        deep_research로 항상 최신성을 검증한다.

═══════════════════════════════════════════════════════════════"""


# Agent-specific wrappers (if an agent needs the protocol formatted differently)
CLAUDE_SYSTEM_PROMPT_APPENDIX = f"""

{RESEARCH_PROTOCOL}
"""

CURSOR_RULES_APPENDIX = f"""

# maru-deep-pro-search Research Protocol
{RESEARCH_PROTOCOL}
"""

KIMI_SKILL_PROMPT = RESEARCH_PROTOCOL

WINDSURF_RULES_APPENDIX = CURSOR_RULES_APPENDIX


def get_protocol_for_agent(agent: str) -> str:
    """Return the research protocol formatted for the given agent."""
    mapping = {
        "claude": CLAUDE_SYSTEM_PROMPT_APPENDIX,
        "cursor": CURSOR_RULES_APPENDIX,
        "windsurf": WINDSURF_RULES_APPENDIX,
        "kimi": KIMI_SKILL_PROMPT,
        "antigravity": RESEARCH_PROTOCOL,
        "kilo": RESEARCH_PROTOCOL,
        "opencode": RESEARCH_PROTOCOL,
    }
    return mapping.get(agent, RESEARCH_PROTOCOL)
