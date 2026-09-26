"""Bespoke executive presentation tab for contract risk assessment, contradiction detection, and clause auditing."""

import html
from typing import Any, Dict, List, Optional

import streamlit as st

from services.risk_service import audit_contract_risks
from ui.components import render_status_region, render_tag


def render_risks_tab(document_text: Optional[str]) -> None:
    """Render Tab 2: Executive Risk Radar, Internal Inconsistencies, and Verified Clause Studio."""
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
            <div>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #00f2fe; text-transform: uppercase; letter-spacing: 0.1em;">
                    Section 02 // Exposure & Vulnerability
                </span>
                <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 800; margin: 4px 0 0 0; color: #ffffff; letter-spacing: -0.02em;">
                    Contract Risk Radar & Clause Studio
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
                <div style="font-size: 2.5rem; margin-bottom: 12px;">🛡️</div>
                <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.3rem; color: #f8fafc; margin-bottom: 6px;">No Contract Ingested</h3>
                <p style="color: #94a3b8; font-size: 0.95rem; max-width: 480px; margin: 0 auto;">
                    Select a contract preset or upload your document to execute the multi-clause vulnerability audit.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    cache_key = f"risk_{st.session_state.get('doc_a_sig', 'doc')}"
    run_btn = st.button("🛡️ Execute Comprehensive Risk Audit", type="primary")

    if run_btn or cache_key in st.session_state:
        if run_btn or cache_key not in st.session_state:
            with st.spinner("Executing risk heuristics, parsing liabilities, and running quote verification..."):
                try:
                    result = audit_contract_risks(document_text)
                    st.session_state[cache_key] = result
                    st.session_state["risk_data"] = result
                    render_status_region("Risk audit complete.")
                except Exception as exc:
                    st.error(f"Audit failed: {exc}")
                    return

        data = st.session_state[cache_key]
        score = data.get("risk_score", 0)
        level = data.get("risk_level", "Medium")
        rationale = data.get("score_rationale", "")
        inconsistencies = data.get("inconsistencies", [])
        clauses: List[Dict[str, Any]] = data.get("clauses", [])

        # Color token resolution
        accent_color = "#10b981" if level == "Low" else ("#f59e0b" if level == "Medium" else "#ef4444")
        bg_glow = "rgba(16, 185, 129, 0.1)" if level == "Low" else ("rgba(245, 158, 11, 0.1)" if level == "Medium" else "rgba(239, 68, 68, 0.15)")

        # 1. Executive Risk Radar Hero HUD
        col_radar, col_rationale = st.columns([1, 2], gap="medium")
        with col_radar:
            st.markdown(
                f"""
                <div class="studio-card" style="text-align: center; background: {bg_glow}; border-color: {accent_color};">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.12em;">
                        AGGREGATE RISK INDEX
                    </div>
                    <div style="font-family: 'Outfit', sans-serif; font-size: 3.8rem; font-weight: 900; color: {accent_color}; line-height: 1; margin: 12px 0 6px 0; text-shadow: 0 0 30px {accent_color}66;">
                        {score}<span style="font-size: 1.4rem; color: #64748b; font-weight: 600;">/100</span>
                    </div>
                    <div>
                        {render_tag(f"{level.upper()} EXPOSURE", level.lower())}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_rationale:
            st.markdown(
                f"""
                <div class="studio-card" style="height: 100%;">
                    <div class="studio-header">
                        <span>🔍 Risk Scoring Assessment</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b;">
                            SYSTEM AUDIT RESULT
                        </span>
                    </div>
                    <p style="font-size: 1.02rem; color: #e2e8f0; line-height: 1.7; margin: 0;">
                        {html.escape(rationale)}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 2. Inconsistencies & Contradiction Inspector
        if inconsistencies:
            st.markdown(
                """
                <div style="font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 700; color: #f87171; margin: 24px 0 12px 0;">
                    ⚠️ Internal Contract Contradictions & Ambiguities Detected
                </div>
                """,
                unsafe_allow_html=True,
            )
            for inc in inconsistencies:
                desc = inc.get("description", "")
                conflicts = inc.get("conflicting_sections", "")
                sev = inc.get("severity", "Medium")
                st.markdown(
                    f"""
                    <div style="background: rgba(69, 10, 10, 0.4); border: 1px solid rgba(239, 68, 68, 0.4); border-left: 4px solid #ef4444; border-radius: 0 10px 10px 0; padding: 14px 18px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <strong style="color: #fca5a5; font-size: 0.95rem;">Contradiction [{sev.upper()} SEVERITY]</strong>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #f87171;">SECTIONS IN CONFLICT: {html.escape(conflicts)}</span>
                        </div>
                        <p style="margin: 0; font-size: 0.9rem; color: #fecaca; line-height: 1.5;">
                            {html.escape(desc)}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                """
                <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 12px 18px; margin: 18px 0; font-size: 0.9rem; color: #a7f3d0; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.1rem;">✓</span>
                    <span><strong>Contradiction Check Clear:</strong> No internal timeline discrepancies or contradictory clauses found in this agreement.</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 3. Interactive Clause Studio with Filters
        st.markdown(
            """
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 700; color: #ffffff; margin: 24px 0 12px 0;">
                Audited Clause Breakdown & Quote Verification
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            category_filter = st.selectbox(
                "Filter by Clause Category",
                options=["All Categories", "Payment", "Termination", "Liability", "Privacy", "Penalty", "Renewal", "Other"],
                index=0,
            )
        with col_f2:
            risk_filter = st.selectbox(
                "Filter by Risk Severity",
                options=["All Severities", "High", "Medium", "Low"],
                index=0,
            )

        filtered = clauses
        if category_filter != "All Categories":
            filtered = [c for c in filtered if c.get("category") == category_filter]
        if risk_filter != "All Severities":
            filtered = [c for c in filtered if c.get("risk_level") == risk_filter]

        if not filtered:
            st.info("No clauses matched the selected filter criteria.")
            return

        for idx, clause in enumerate(filtered):
            title = clause.get("title", f"Clause {idx + 1}")
            cat = clause.get("category", "Other")
            r_level = clause.get("risk_level", "Medium")
            expl = clause.get("risk_explanation", "")
            quote = clause.get("quote", "")
            counter = clause.get("counter_proposal", "")
            ver = clause.get("verification", {})
            v_status = ver.get("status", "UNVERIFIED")
            v_score = ver.get("score", 0)

            if v_status == "VERIFIED":
                v_tag = f'<span class="tag-pill tag-verified">🛡️ VERIFIED QUOTE ({v_score}%)</span>'
            elif v_status == "PARTIAL_MATCH":
                v_tag = f'<span class="tag-pill tag-medium">~ PARTIAL ({v_score}%)</span>'
            else:
                v_tag = f'<span class="tag-pill tag-high">✗ UNVERIFIED ({v_score}%)</span>'

            sev_tag = render_tag(f"{r_level} Exposure", r_level.lower())
            cat_tag = f'<span style="font-family: \'JetBrains Mono\', monospace; font-size: 0.72rem; color: #94a3b8; background: rgba(255, 255, 255, 0.05); padding: 3px 8px; border-radius: 4px; border: 1px solid rgba(255, 255, 255, 0.08);">{html.escape(cat)}</span>'

            st.markdown(
                f"""
                <div class="studio-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: #ffffff;">
                            {html.escape(title)}
                        </span>
                        <div style="display: flex; gap: 8px; align-items: center;">
                            {cat_tag}
                            {sev_tag}
                            {v_tag}
                        </div>
                    </div>
                    <div style="font-size: 0.95rem; color: #cbd5e1; line-height: 1.6; margin-bottom: 8px;">
                        <strong style="color: #f8fafc;">Vulnerability Analysis:</strong> {html.escape(expl)}
                    </div>
                    <div class="studio-quote">
                        "{html.escape(quote)}"
                    </div>
                    <div class="studio-counter">
                        <strong style="color: #34d399;">Recommended Counter-Proposal:</strong><br>
                        {html.escape(counter)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
