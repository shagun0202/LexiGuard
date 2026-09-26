"""Ultra-modern, executive presentation tab for document simplification and deal terms."""

import html
from typing import Optional

import streamlit as st

from services.simplify_service import simplify_document
from ui.components import render_status_region, render_tag


def render_simplify_tab(
    document_text: Optional[str],
    reading_level: str = "standard",
    language: str = "english",
) -> None:
    """Render Tab 1: Executive Deal Summary, Commercial Takeaways, and Plain-English Lexicon."""
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
            <div>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #00f2fe; text-transform: uppercase; letter-spacing: 0.1em;">
                    Section 01 // Clarity Studio
                </span>
                <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 800; margin: 4px 0 0 0; color: #ffffff; letter-spacing: -0.02em;">
                    Executive Deal Summary & Plain-Language Lexicon
                </h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not document_text:
        st.markdown(
            """
            <div class="studio-card" style="text-align: center; padding: 40px 20px;">
                <div style="font-size: 2.5rem; margin-bottom: 12px;">📂</div>
                <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.3rem; color: #f8fafc; margin-bottom: 6px;">No Contract Ingested</h3>
                <p style="color: #94a3b8; font-size: 0.95rem; max-width: 480px; margin: 0 auto;">
                    Select a sample preset or drag and drop your PDF / DOCX agreement in the left Control Deck to initiate analysis.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    cache_key = f"simplify_{st.session_state.get('doc_a_sig', 'doc')}_{reading_level}_{language}"
    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        run_btn = st.button("⚡ Synthesize Plain-Language Brief", type="primary", use_container_width=True)
    with col_info:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; height: 100%; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #94a3b8;">
                <span>ACTIVE PERSONA: <strong style="color: #00f2fe;">{reading_level.upper()}</strong></span> • 
                <span>LANG: <strong style="color: #f8fafc;">{language.upper()}</strong></span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if run_btn or cache_key in st.session_state:
        if run_btn or cache_key not in st.session_state:
            with st.spinner("Decoding legalese, distilling key rights, and building plain-English lexicon..."):
                try:
                    result = simplify_document(
                        document_text=document_text,
                        reading_level=reading_level,
                        language=language,
                    )
                    st.session_state[cache_key] = result
                    st.session_state["simplify_data"] = result
                    render_status_region("Simplification brief ready.")
                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")
                    return

        data = st.session_state[cache_key]
        summary_text = data.get("summary", "")
        key_points = data.get("key_points", [])
        glossary = data.get("glossary", [])

        # Executive Briefing Card
        st.markdown(
            f"""
            <div class="studio-card" style="margin-top: 14px;">
                <div class="studio-header">
                    <span>📋 Executive Deal Brief</span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #00f2fe; background: rgba(0, 242, 254, 0.1); border: 1px solid rgba(0, 242, 254, 0.3); padding: 3px 8px; border-radius: 6px;">
                        TRANSFORMED TO PLAIN ENGLISH
                    </span>
                </div>
                <p style="font-size: 1.08rem; line-height: 1.7; color: #f1f5f9; margin: 0; font-weight: 400;">
                    {html.escape(summary_text)}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_left, col_right = st.columns([1, 1], gap="medium")

        # Column 1: Key Commercial & Legal Takeaways
        with col_left:
            st.markdown(
                """
                <div style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: #ffffff; margin: 16px 0 12px 0;">
                    🎯 Key Commercial & Operational Takeaways
                </div>
                """,
                unsafe_allow_html=True,
            )
            for idx, pt in enumerate(key_points, start=1):
                st.markdown(
                    f"""
                    <div style="background: rgba(13, 20, 36, 0.65); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 14px 18px; margin-bottom: 10px; display: flex; gap: 14px; align-items: flex-start;">
                        <span style="background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%); color: #050811; font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 0.8rem; width: 24px; height: 24px; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px;">
                            {idx}
                        </span>
                        <span style="font-size: 0.95rem; color: #e2e8f0; line-height: 1.5;">
                            {html.escape(pt)}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Column 2: Plain-Language Legal Glossary Cards
        with col_right:
            st.markdown(
                """
                <div style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: #ffffff; margin: 16px 0 12px 0;">
                    📖 Plain-Language Legal Lexicon
                </div>
                """,
                unsafe_allow_html=True,
            )
            for item in glossary:
                term = item.get("term", "")
                defn = item.get("definition", "")
                ctx = item.get("context", "")

                st.markdown(
                    f"""
                    <div style="background: rgba(13, 20, 36, 0.65); border: 1px solid rgba(255, 255, 255, 0.06); border-left: 3px solid #00f2fe; border-radius: 0 12px 12px 0; padding: 14px 18px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1rem; color: #00f2fe;">
                                {html.escape(term)}
                            </span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #64748b; text-transform: uppercase;">
                                LEGALESE TRANSLATION
                            </span>
                        </div>
                        <div style="font-size: 0.92rem; color: #f8fafc; font-weight: 500; margin-bottom: 6px; line-height: 1.4;">
                            {html.escape(defn)}
                        </div>
                        <div style="font-family: Georgia, serif; font-style: italic; font-size: 0.82rem; color: #94a3b8; border-top: 1px solid rgba(255, 255, 255, 0.04); padding-top: 6px;">
                            Context: "{html.escape(ctx)}"
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
