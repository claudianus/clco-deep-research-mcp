"""Tests for token default changes."""

import inspect

from maru_search.tools import (
    tool_fetch_page,
    tool_fetch_bulk,
    tool_stealthy_fetch,
    TOOLS,
)
from maru_search.research.deep import format_for_llm


class TestTokenDefaults:
    def test_fetch_page_default_increased(self):
        sig = inspect.signature(tool_fetch_page)
        default = sig.parameters['max_tokens'].default
        assert default == 6000, f"Expected 6000, got {default}"

    def test_fetch_bulk_default_increased(self):
        sig = inspect.signature(tool_fetch_bulk)
        default = sig.parameters['max_tokens'].default
        assert default == 3000, f"Expected 3000, got {default}"

    def test_stealthy_fetch_default_increased(self):
        sig = inspect.signature(tool_stealthy_fetch)
        default = sig.parameters['max_tokens'].default
        assert default == 6000, f"Expected 6000, got {default}"

    def test_format_for_llm_default_increased(self):
        sig = inspect.signature(format_for_llm)
        default = sig.parameters['max_tokens_per_source'].default
        assert default == 2500, f"Expected 2500, got {default}"

    def test_maximum_bounds_unchanged(self):
        schema = TOOLS["fetch_page"][2]["properties"]["max_tokens"]
        assert schema["maximum"] == 8000
        schema = TOOLS["fetch_bulk"][2]["properties"]["max_tokens"]
        assert schema["maximum"] == 5000

    def test_tool_registry_defaults_updated(self):
        assert TOOLS["fetch_page"][2]["properties"]["max_tokens"]["default"] == 6000
        assert TOOLS["fetch_bulk"][2]["properties"]["max_tokens"]["default"] == 3000
        assert TOOLS["stealthy_fetch"][2]["properties"]["max_tokens"]["default"] == 6000
