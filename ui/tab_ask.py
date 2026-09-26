"""Bespoke presentation tab for grounded interactive contract interrogation and counsel alerts."""

import html
from typing import Optional

import streamlit as st

from services.qa_service import answer_document_query
from ui.components import render_status_region


def render_ask_tab(document_text: Optional[str]) -> None:
    """Render Tab 3: Interactive Grounded Interrogation Studio with Quote Verification."""
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
            <div>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #00f2fe; text-transform: uppercase; letter-spacing: 0.1em;">
                    Section 03 // Interrogation Studio
                </span>
                <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 800; margin: 4px 0 0 0; color: #ffffff; letter-spacing: -0.02em;">
                    Grounded Contract Interrogation Lab
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
                <div style="font-size: 2.5rem; margin-bottom: 12px;">💬</div>
                <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.3rem; color: #f8fafc; margin-bottom: 6px;">No Contract Ingested</h3>
                <p style="color: #94a3b8; font-size: 0.95rem; max-width: 480px; margin: 0 auto;">
                    Select a contract preset or upload your document to interrogate clauses with strict textual grounding.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    if "qa_messages" not in st.session_state:
        st.session_state["qa_messages"] = []

    # Quick Interrogation Prompts Deck
    st.markdown(
        """
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">
            QUICK INTERROGATION PRESETS
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3, col4 = st.columns(4)
    suggested_q = None

    if col1.button("🚪 Termination Triggers", use_container_width=True):
        suggested_q = "Under what exact conditions and notice windows can either party terminate this contract?"
    if col2.button("💰 Liability & Indemnity", use_container_width=True):
        suggested_q = "What is the monetary liability cap and are there any carve-outs or indemnification duties?"
    if col3.button("🔒 Confidentiality Scope", use_container_width=True):
        suggested_q = "What is the duration of confidentiality and how are trade secrets treated?"
    if col4.button("⚖️ Arbitration & Venue", use_container_width=True):
        suggested_q = "What is the governing law, venue, and is there a mandatory arbitration clause?"

    # Conversation Display
    for msg in st.session_state["qa_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)
            if "quotes" in msg and msg["quotes"]:
                with st.expander("Supporting Grounded Citations"):
                    for q_item in msg["quotes"]:
                        quote_str = q_item.get("quote", str(q_item))
                        ver = q_item.get("verification", {})
                        status = ver.get("status", "VERIFIED")
                        score = ver.get("score", 100)
                        st.markdown(
                            f"""
                            <div class="studio-quote">
                                "{html.escape(quote_str)}"
                                <div style="margin-top: 6px; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #00f2fe;">
                                    AUTHENTICITY STATUS: {status} ({score}% MATCH)
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            if msg.get("needs_lawyer"):
                rationale = msg.get("lawyer_rationale", "This inquiry touches on critical legal liability.")
                st.markdown(
                    f"""
                    <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.4); border-left: 4px solid #f59e0b; padding: 12px 18px; border-radius: 0 10px 10px 0; margin-top: 10px; color: #fde68a; font-size: 0.88rem;">
                        <strong>⚠️ ATTORNEY CONSULTATION PROTOCOL ACTIVATED:</strong><br>
                        {html.escape(rationale)}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    user_query = st.chat_input("Enter legal inquiry strictly grounded in this contract...")
    prompt_to_run = suggested_q or user_query

    if prompt_to_run:
        st.session_state["qa_messages"].append({"role": "user", "content": prompt_to_run})
        with st.chat_message("user"):
            st.markdown(html.escape(prompt_to_run))

        with st.chat_message("assistant"):
            with st.spinner("Searching document index and verifying citations..."):
                try:
                    qa_res = answer_document_query(
                        document_text=document_text,
                        question=prompt_to_run,
                        chat_history=st.session_state["qa_messages"],
                    )
                    answer_text = qa_res.get("answer", "Not specified in document.")
                    verified_quotes = qa_res.get("verified_quotes", [])
                    needs_lawyer = qa_res.get("needs_lawyer", False)
                    lawyer_rationale = qa_res.get("lawyer_rationale", "")

                    st.markdown(answer_text)

                    if verified_quotes:
                        with st.expander("Supporting Grounded Citations"):
                            for q_item in verified_quotes:
                                quote_str = q_item.get("quote", "")
                                ver = q_item.get("verification", {})
                                status = ver.get("status", "VERIFIED")
                                score = ver.get("score", 100)
                                st.markdown(
                                    f"""
                                    <div class="studio-quote">
                                        "{html.escape(quote_str)}"
                                        <div style="margin-top: 6px; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #00f2fe;">
                                            AUTHENTICITY STATUS: {status} ({score}% MATCH)
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                    if needs_lawyer:
                        st.markdown(
                            f"""
                            <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.4); border-left: 4px solid #f59e0b; padding: 12px 18px; border-radius: 0 10px 10px 0; margin-top: 10px; color: #fde68a; font-size: 0.88rem;">
                                <strong>⚠️ ATTORNEY CONSULTATION PROTOCOL ACTIVATED:</strong><br>
                                {html.escape(lawyer_rationale)}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    st.session_state["qa_messages"].append({
                        "role": "assistant",
                        "content": answer_text,
                        "quotes": verified_quotes,
                        "needs_lawyer": needs_lawyer,
                        "lawyer_rationale": lawyer_rationale,
                    })
                    render_status_region("Response generated.")

                except Exception as exc:
                    st.error(f"Interrogation failed: {exc}")

    if st.session_state["qa_messages"]:
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Interrogation Transcript"):
            st.session_state["qa_messages"] = []
            st.rerun()
