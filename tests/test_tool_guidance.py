"""Tests for tool guidance and MCP prompts."""

from maru_deep_pro_search.tools import TOOL_GUIDANCE, TOOLS


class TestToolGuidance:
    def test_tool_guidance_exists(self):
        assert TOOL_GUIDANCE is not None
        assert len(TOOL_GUIDANCE) > 0
        assert "Tool Selection Guide" in TOOL_GUIDANCE

    def test_tool_guidance_has_decision_tree(self):
        assert "Decision Tree" in TOOL_GUIDANCE

    def test_tool_guidance_has_performance_tips(self):
        assert "Performance" in TOOL_GUIDANCE or "performance" in TOOL_GUIDANCE

    def test_tool_guidance_has_common_mistakes(self):
        assert "Common Mistakes" in TOOL_GUIDANCE or "mistakes" in TOOL_GUIDANCE.lower()


class TestEnhancedToolDescriptions:
    def test_web_search_has_best_for(self):
        desc = TOOLS["web_search"][1]
        assert "BEST FOR" in desc

    def test_fetch_page_has_try_first(self):
        desc = TOOLS["fetch_page"][1]
        assert "TRY FIRST" in desc

    def test_stealthy_fetch_has_last_resort(self):
        desc = TOOLS["stealthy_fetch"][1]
        assert "LAST RESORT" in desc or "last resort" in desc.lower()

    def test_deep_research_has_not_for(self):
        desc = TOOLS["deep_research"][1]
        assert "NOT FOR" in desc

    def test_parallel_search_has_best_for(self):
        desc = TOOLS["parallel_search"][1]
        assert "BEST FOR" in desc

    def test_fetch_bulk_has_best_for(self):
        desc = TOOLS["fetch_bulk"][1]
        assert "BEST FOR" in desc

    def test_all_tools_have_enhanced_descriptions(self):
        for tool_name, (_func, desc, _schema) in TOOLS.items():
            assert len(desc) > 50, f"{tool_name} description too short"
            assert "BEST FOR" in desc or "best for" in desc.lower(), f"{tool_name} missing BEST FOR"
