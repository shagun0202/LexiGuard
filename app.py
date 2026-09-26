"""LexiGuard: Enterprise AI Legal Document Intelligence & Risk Engine.

Main application entry point orchestrating layout, modular presentation tabs,
and session state routing. Strictly non-monolithic orchestrator under 80 lines.
"""

import os
import streamlit as st

# Sync Streamlit Cloud secrets to os.environ on startup
try:
    if hasattr(st, "secrets"):
        for k in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
            if k in st.secrets and st.secrets[k]:
                os.environ[k] = str(st.secrets[k]).strip()
except Exception:
    pass

from ui import (
    inject_custom_css,
    render_action_plan_tab,
    render_ask_tab,
    render_compare_tab,
    render_footer,
    render_header,
    render_risks_tab,
    render_sidebar,
    render_simplify_tab,
    render_skip_link,
)

# 1. Page Configuration
st.set_page_config(
    page_title="LexiGuard - AI Legal Document Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Inject WCAG 2.1 AA/AAA CSS Tokens & Skip-Link
inject_custom_css()
render_skip_link()

# 3. Render Application Header & Educational Disclaimer
render_header()

# 4. Render Sidebar Controls
doc_a_text, doc_a_name, doc_b_text, doc_b_name, reading_level, language = render_sidebar()

# 5. Modular Tab Routing
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. 📄 Deal Clarity Brief",
    "2. 🛡️ Risk & Clause Studio",
    "3. 💬 Interrogation Lab",
    "4. ⚖️ Redline Matrix",
    "5. 📋 Execution Command",
])

with tab1:
    render_simplify_tab(doc_a_text, reading_level=reading_level, language=language)

with tab2:
    render_risks_tab(doc_a_text)

with tab3:
    render_ask_tab(doc_a_text)

with tab4:
    render_compare_tab(doc_a_text, doc_a_name, doc_b_text, doc_b_name)

with tab5:
    render_action_plan_tab(doc_a_text, doc_a_name)

# 6. Render Footer
render_footer()
