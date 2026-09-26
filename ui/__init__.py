"""Modular presentation layer for LexiGuard."""

from ui.components import inject_custom_css, render_footer, render_header, render_skip_link
from ui.sidebar import render_sidebar
from ui.tab_action_plan import render_action_plan_tab
from ui.tab_ask import render_ask_tab
from ui.tab_compare import render_compare_tab
from ui.tab_risks import render_risks_tab
from ui.tab_simplify import render_simplify_tab

__all__ = [
    "inject_custom_css",
    "render_skip_link",
    "render_header",
    "render_footer",
    "render_sidebar",
    "render_simplify_tab",
    "render_risks_tab",
    "render_ask_tab",
    "render_compare_tab",
    "render_action_plan_tab",
]
