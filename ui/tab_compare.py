"""Bespoke presentation tab for dual contract redline comparison and favorability matrix."""

import html
from typing import Optional

import streamlit as st

from services.compare_service import compare_documents
from ui.components import render_status_region, render_tag


def render_compare_tab(
    doc_a_text: Optional[str],
    doc_a_name: Optional[str],
    doc_b_text: Optional[str],
    doc_b_name: Optional[str],
) -> None:
    """Render Tab 4: Dual Contract Redline Deck & Asymmetric Favorability Matrix."""
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
            <div>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #00f2fe; text-transform: uppercase; letter-spacing: 0.1em;">
                    Section 04 // Redline Matrix
                </span>
                <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 800; margin: 4px 0 0 0; color: #ffffff; letter-spacing: -0.02em;">
                    Dual Contract Comparison & Favorability Matrix
                </h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not doc_a_text:
        st.markdown(
            """
            <div class="studio-card" style="text-align: center; padding: 40px 20px;">
                <div style="font-size: 2.5rem; margin-bottom: 12px;">⚖️</div>
                <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.3rem; color: #f8fafc; margin-bottom: 6px;">No Baseline Ingested</h3>
                <p style="color: #94a3b8; font-size: 0.95rem; max-width: 480px; margin: 0 auto;">
                    Please ingest Document A in the left Control Deck before initiating contract comparison.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    if not doc_b_text:
        st.markdown(
            """
            <div class="studio-card" style="border-color: rgba(192, 132, 252, 0.4); background: rgba(88, 28, 135, 0.1);">
                <div style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: #c084fc; margin-bottom: 6px;">
                    📑 Dual Redline Mode Awaiting Secondary Agreement
                </div>
                <p style="font-size: 0.95rem; color: #e9d5ff; margin: 0;">
                    To compare two versions or counterparty redlines, toggle <strong>'Dual Redline Mode (Doc B)'</strong> in the left Control Deck and upload Document B.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    name_a = doc_a_name or "Document A"
    name_b = doc_b_name or "Document B"

    # Comparison Ingestion Header Tiles
    st.markdown(
        f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;">
            <div class="hud-tile" style="border-left: 3px solid #00f2fe;">
                <div class="hud-tile-label">BASELINE SPECIFICATION (DOC A)</div>
                <div style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.1rem; color: #f8fafc;">{html.escape(name_a)}</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; margin-top: 4px;">LENGTH: {len(doc_a_text):,} CHARACTERS</div>
            </div>
            <div class="hud-tile" style="border-left: 3px solid #c084fc;">
                <div class="hud-tile-label">COUNTERPARTY / REVISED (DOC B)</div>
                <div style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.1rem; color: #f8fafc;">{html.escape(name_b)}</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; margin-top: 4px;">LENGTH: {len(doc_b_text):,} CHARACTERS</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cache_key = f"compare_{st.session_state.get('doc_a_sig', 'a')}_{st.session_state.get('doc_b_sig', 'b')}"
    run_btn = st.button("⚖️ Run Comparative Redline Audit", type="primary")

    if run_btn or cache_key in st.session_state:
        if run_btn or cache_key not in st.session_state:
            with st.spinner("Aligning clause taxonomies, computing favorability balance, and mapping omissions..."):
                try:
                    res = compare_documents(doc_a_text, doc_b_text)
                    st.session_state[cache_key] = res
                    render_status_region("Comparison complete.")
                except Exception as exc:
                    st.error(f"Comparison failed: {exc}")
                    return

        data = st.session_state[cache_key]
        overall = data.get("overall_comparison", "")
        favorability = data.get("favorability", "Neither / Balanced")
        differences = data.get("differences", [])
        missing_a = data.get("missing_in_doc_a", [])
        missing_b = data.get("missing_in_doc_b", [])

        # Executive Favorability Verdict Banner
        fav_color = "#00f2fe" if "A" in favorability else ("#c084fc" if "B" in favorability else "#10b981")
        st.markdown(
            f"""
            <div class="studio-card" style="border-left: 5px solid {fav_color};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 800; color: #ffffff;">
                        Strategic Advantage Assessment
                    </span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; font-weight: 700; color: {fav_color}; background: rgba(0,0,0,0.4); border: 1px solid {fav_color}; padding: 4px 14px; border-radius: 9999px;">
                        ADVANTAGE: {html.escape(favorability.upper())}
                    </span>
                </div>
                <p style="font-size: 1.02rem; color: #cbd5e1; line-height: 1.7; margin: 0;">
                    {html.escape(overall)}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Side-by-Side Clause Matrix
        if differences:
            st.markdown(
                """
                <div style="font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 700; color: #ffffff; margin: 24px 0 12px 0;">
                    Substantive Clause Provisions Breakdown
                </div>
                """,
                unsafe_allow_html=True,
            )
            for diff in differences:
                topic = diff.get("clause_topic", "")
                p_a = diff.get("doc_a_provision", "")
                p_b = diff.get("doc_b_provision", "")
                more_fav = diff.get("more_favorable_to", "Equal")
                analysis = diff.get("analysis", "")

                adv_color = "#00f2fe" if "A" in more_fav else ("#c084fc" if "B" in more_fav else "#94a3b8")

                st.markdown(
                    f"""
                    <div class="studio-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <span style="font-family: 'Outfit', sans-serif; font-size: 1.1rem; font-weight: 700; color: #ffffff;">
                                {html.escape(topic)}
                            </span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: {adv_color}; border: 1px solid {adv_color}; padding: 2px 10px; border-radius: 9999px;">
                                FAVORABLE: {html.escape(more_fav.upper())}
                            </span>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 12px 0;">
                            <div style="background: rgba(6, 10, 20, 0.7); padding: 12px 16px; border-radius: 8px; border-left: 3px solid #00f2fe;">
                                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #00f2fe; margin-bottom: 4px;">DOC A (BASELINE)</div>
                                <div style="font-size: 0.92rem; color: #e2e8f0; line-height: 1.5;">{html.escape(p_a)}</div>
                            </div>
                            <div style="background: rgba(6, 10, 20, 0.7); padding: 12px 16px; border-radius: 8px; border-left: 3px solid #c084fc;">
                                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #c084fc; margin-bottom: 4px;">DOC B (COUNTERPARTY)</div>
                                <div style="font-size: 0.92rem; color: #e2e8f0; line-height: 1.5;">{html.escape(p_b)}</div>
                            </div>
                        </div>
                        <div style="font-size: 0.88rem; color: #94a3b8; border-top: 1px solid rgba(255, 255, 255, 0.04); padding-top: 8px;">
                            <strong style="color: #cbd5e1;">Strategic Analysis:</strong> {html.escape(analysis)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Missing Clause Asymmetry Detection
        st.markdown(
            """
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 700; color: #ffffff; margin: 24px 0 12px 0;">
                Omission & Clause Asymmetry Detection
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_m1, col_m2 = st.columns(2, gap="medium")
        with col_m1:
            st.markdown(
                f"""
                <div class="hud-tile" style="border-top: 3px solid #f87171;">
                    <div style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 0.95rem; color: #fca5a5; margin-bottom: 8px;">
                        PROTECTIONS MISSING IN {html.escape(name_a.upper())}
                    </div>
                """,
                unsafe_allow_html=True,
            )
            if missing_a:
                for item in missing_a:
                    st.markdown(f"<div style='font-size: 0.88rem; color: #fecaca; margin-bottom: 6px;'>• {html.escape(item)}</div>", unsafe_allow_html=True)
            else:
                st.caption("No asymmetric omissions detected.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_m2:
            st.markdown(
                f"""
                <div class="hud-tile" style="border-top: 3px solid #f87171;">
                    <div style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 0.95rem; color: #fca5a5; margin-bottom: 8px;">
                        PROTECTIONS MISSING IN {html.escape(name_b.upper())}
                    </div>
                """,
                unsafe_allow_html=True,
            )
            if missing_b:
                for item in missing_b:
                    st.markdown(f"<div style='font-size: 0.88rem; color: #fecaca; margin-bottom: 6px;'>• {html.escape(item)}</div>", unsafe_allow_html=True)
            else:
                st.caption("No asymmetric omissions detected.")
            st.markdown("</div>", unsafe_allow_html=True)
