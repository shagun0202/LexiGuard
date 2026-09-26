"""Bespoke presentation tab for pre-execution action plan, milestones, and Word dossier export."""

import html
from typing import Optional

import streamlit as st

from services.action_service import generate_action_plan
from ui.components import render_status_region
from utils.doc_exporter import export_to_docx


def render_action_plan_tab(
    document_text: Optional[str],
    document_name: Optional[str],
) -> None:
    """Render Tab 5: Executive Pre-Flight Action Plan, Milestones, and Word Dossier Export."""
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
            <div>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #00f2fe; text-transform: uppercase; letter-spacing: 0.1em;">
                    Section 05 // Action Command
                </span>
                <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 800; margin: 4px 0 0 0; color: #ffffff; letter-spacing: -0.02em;">
                    Pre-Flight Execution Plan & Counsel Dossier
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
                <div style="font-size: 2.5rem; margin-bottom: 12px;">📋</div>
                <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.3rem; color: #f8fafc; margin-bottom: 6px;">No Contract Ingested</h3>
                <p style="color: #94a3b8; font-size: 0.95rem; max-width: 480px; margin: 0 auto;">
                    Ingest a contract in the left Control Deck to synthesize execution checklists, deadlines, and export Word dossiers.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    cache_key = f"action_{st.session_state.get('doc_a_sig', 'doc')}"
    run_btn = st.button("📋 Synthesize Pre-Flight Action Plan", type="primary")

    if run_btn or cache_key in st.session_state:
        if run_btn or cache_key not in st.session_state:
            with st.spinner("Extracting obligations, compiling pre-execution verifications, and generating counsel briefing..."):
                try:
                    res = generate_action_plan(document_text)
                    st.session_state[cache_key] = res
                    st.session_state["action_data"] = res
                    render_status_region("Action plan generated.")
                except Exception as exc:
                    st.error(f"Action plan failed: {exc}")
                    return

        data = st.session_state[cache_key]
        checklist = data.get("checklist", [])
        deadlines = data.get("deadlines", [])
        questions = data.get("lawyer_questions", [])

        # 1. Executive Word (.docx) Dossier Export Hero Card
        st.markdown(
            """
            <div class="studio-card" style="border-left: 4px solid #00f2fe; margin-top: 14px;">
                <div class="studio-header">
                    <span>📄 Executive Legal Dossier (.docx)</span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #00f2fe; background: rgba(0, 242, 254, 0.1); padding: 3px 8px; border-radius: 4px;">
                        BOARDROOM FORMAT
                    </span>
                </div>
                <p style="font-size: 0.95rem; color: #94a3b8; margin: 0 0 16px 0;">
                    Export the entire analytical assessment—including executive summary, risk scores, contradiction warnings, verified clause quotes, counter-proposals, and attorney consultation prep—into a beautifully formatted Microsoft Word report.
                </p>
            """,
            unsafe_allow_html=True,
        )

        docx_cache_key = f"docx_bytes_{st.session_state.get('doc_a_sig', 'doc')}"
        if docx_cache_key not in st.session_state or run_btn:
            summary_data = st.session_state.get("simplify_data")
            risk_data = st.session_state.get("risk_data")
            doc_name = document_name or "Legal_Agreement.docx"
            try:
                docx_bytes = export_to_docx(
                    document_name=doc_name,
                    summary_data=summary_data,
                    risk_data=risk_data,
                    action_data=data,
                )
                st.session_state[docx_cache_key] = docx_bytes
            except Exception as exc:
                st.warning(f"Could not build Word export: {exc}")

        if docx_cache_key in st.session_state:
            filename = f"LexiGuard_Dossier_{document_name or 'Contract'}.docx"
            st.download_button(
                label="⬇️ Download Executive Legal Dossier (.docx)",
                data=st.session_state[docx_cache_key],
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1], gap="medium")

        # 2. Interactive Pre-Flight Checklist
        with col_left:
            st.markdown(
                """
                <div style="font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 700; color: #ffffff; margin: 20px 0 12px 0;">
                    ✓ Pre-Flight Signing Verification Checklist
                </div>
                """,
                unsafe_allow_html=True,
            )

            checklist_state_key = f"checklist_checks_{st.session_state.get('doc_a_sig', 'doc')}"
            if checklist_state_key not in st.session_state:
                st.session_state[checklist_state_key] = {i: False for i in range(len(checklist))}

            completed_count = sum(1 for v in st.session_state[checklist_state_key].values() if v)
            total_count = len(checklist)

            st.caption(f"Verification Progress: {completed_count} of {total_count} items completed")
            st.progress(completed_count / total_count if total_count > 0 else 0.0)

            for idx, item in enumerate(checklist):
                task_text = item.get("task", str(item)) if isinstance(item, dict) else str(item)
                cat = item.get("category", "General") if isinstance(item, dict) else "General"

                current_val = st.session_state[checklist_state_key].get(idx, False)
                checked = st.checkbox(
                    f"[{cat.upper()}] {task_text}",
                    value=current_val,
                    key=f"chk_{checklist_state_key}_{idx}",
                )
                st.session_state[checklist_state_key][idx] = checked

        # 3. Critical Milestones & Timeline Table
        with col_right:
            st.markdown(
                """
                <div style="font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 700; color: #ffffff; margin: 20px 0 12px 0;">
                    ⏱️ Obligations & Critical Milestones Timeline
                </div>
                """,
                unsafe_allow_html=True,
            )
            for dl in deadlines:
                task = dl.get("task", "")
                who = dl.get("responsible_party", "")
                when = dl.get("deadline", "")
                st.markdown(
                    f"""
                    <div style="background: rgba(13, 20, 36, 0.65); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 12px 16px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-family: 'Outfit', sans-serif; font-weight: 700; color: #ffffff; font-size: 0.95rem;">{html.escape(task)}</span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #00f2fe; background: rgba(0, 242, 254, 0.1); padding: 2px 8px; border-radius: 4px;">{html.escape(when)}</span>
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #94a3b8;">
                            RESPONSIBLE PARTY: <span style="color: #cbd5e1;">{html.escape(who)}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # 4. Targeted Questions for Legal Counsel
        st.markdown(
            """
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 700; color: #ffffff; margin: 30px 0 14px 0;">
                ⚖️ High-Value Consultation Questions for Legal Counsel
            </div>
            """,
            unsafe_allow_html=True,
        )
        for idx, q in enumerate(questions, start=1):
            st.markdown(
                f"""
                <div style="background: rgba(13, 20, 36, 0.7); border: 1px solid rgba(255, 255, 255, 0.07); border-left: 3px solid #38bdf8; border-radius: 0 10px 10px 0; padding: 12px 18px; margin-bottom: 8px; font-size: 0.95rem; color: #f1f5f9; display: flex; gap: 12px; align-items: flex-start;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #00f2fe; font-size: 0.85rem; margin-top: 1px;">Q{idx:02d}</span>
                    <span style="line-height: 1.5;">{html.escape(q)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
