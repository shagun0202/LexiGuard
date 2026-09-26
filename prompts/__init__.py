"""Isolated schemas and prompt builders for LexiGuard AI services."""

from prompts.action import build_action_prompt, get_action_schema
from prompts.compare import build_compare_prompt, get_compare_schema
from prompts.qa import build_qa_prompt, get_qa_schema
from prompts.risk import build_risk_prompt, get_risk_schema
from prompts.simplify import build_simplify_prompt, get_simplify_schema

__all__ = [
    "build_simplify_prompt",
    "get_simplify_schema",
    "build_risk_prompt",
    "get_risk_schema",
    "build_qa_prompt",
    "get_qa_schema",
    "build_compare_prompt",
    "get_compare_schema",
    "build_action_prompt",
    "get_action_schema",
]
