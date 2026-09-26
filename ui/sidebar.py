"""Bespoke studio sidebar navigation, document ingestion, and telemetry deck for LexiGuard."""

from pathlib import Path
from typing import Optional, Tuple

import streamlit as st

from services.gemini_client import get_last_call_info
from utils.file_reader import compute_file_signature, extract_text_from_file
from utils.legal_checker import check_legal_density


def render_sidebar() -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], str, str]:
    """Render high-end studio controls, file ingestion deck, and telemetry."""
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 10px 0 16px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 18px;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #00f2fe; text-transform: uppercase; letter-spacing: 0.14em;">
                    Studio Control Deck
                </div>
                <div style="font-family: 'Outfit', sans-serif; font-size: 1.35rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
                    Contract Ingestion
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 1. Preset Repository Selector
        st.markdown(
            "<span style='font-family: Outfit; font-weight: 700; font-size: 0.88rem; color: #cbd5e1;'>📁 Sample Contract Presets</span>",
            unsafe_allow_html=True,
        )
        sample_choice = st.selectbox(
            "Select Preset",
            options=[
                "Upload Custom Contract",
                "Apex vs Horizon (Mutual NDA)",
                "Zenith Cloud (Executive Employment)",
                "CyberScale Systems (Master SaaS MSA)",
            ],
            index=0,
            label_visibility="collapsed",
            help="Load realistic enterprise legal contracts for instant end-to-end evaluation.",
        )

        sample_paths = {
            "Apex vs Horizon (Mutual NDA)": ("demo_data/sample_nda.txt", "Apex_Horizon_Mutual_NDA.txt"),
            "Zenith Cloud (Executive Employment)": ("demo_data/sample_employment.txt", "Zenith_Executive_Employment.txt"),
            "CyberScale Systems (Master SaaS MSA)": ("demo_data/sample_saas_vendor.txt", "CyberScale_Master_SaaS.txt"),
        }

        # 2. File Ingestion Dock
        st.markdown(
            "<div style='margin-top: 14px;'><span style='font-family: Outfit; font-weight: 700; font-size: 0.88rem; color: #cbd5e1;'>📄 Primary Document Dock (Doc A)</span></div>",
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Primary Agreement (Doc A)",
            type=["pdf", "docx", "txt", "md"],
            label_visibility="collapsed",
            help="Upload PDF, DOCX, or TXT up to 15MB.",
        )

        # Dual Contract Redline Mode
        st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
        enable_compare = st.toggle(
            "Dual Redline Mode (Doc B)",
            value=st.session_state.get("enable_compare", False),
            help="Enable side-by-side comparative analysis with a second contract version in Tab 4.",
        )
        st.session_state["enable_compare"] = enable_compare

        uploaded_file_b = None
        if enable_compare:
            st.markdown(
                "<span style='font-family: Outfit; font-weight: 700; font-size: 0.85rem; color: #c084fc;'>📑 Counterparty / Revised Dock (Doc B)</span>",
                unsafe_allow_html=True,
            )
            uploaded_file_b = st.file_uploader(
                "Secondary Agreement (Doc B)",
                type=["pdf", "docx", "txt", "md"],
                label_visibility="collapsed",
                key="uploader_doc_b",
                help="Upload counterparty revision for comparative audit.",
            )

        # 3. Reading Level & Language Preferences
        st.markdown(
            """
            <div style="margin-top: 20px; padding-top: 14px; border-top: 1px solid rgba(255, 255, 255, 0.06);">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px;">
                    Intelligence Tuning
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        reading_persona = st.radio(
            "Analysis Persona",
            options=["💼 Corporate Executive (Standard)", "🎓 High School Student (ELI15)"],
            index=0,
            help="Standard delivers boardroom-ready plain English; ELI15 breaks terms down with intuitive metaphors.",
        )
        reading_level = "eli15" if "15" in reading_persona else "standard"

        language_choice = st.selectbox(
            "Output Language",
            options=["English (Default)", "हिंदी (Hindi)", "ಕನ್ನಡ (Kannada)"],
            index=0,
            help="Translate explanations, summaries, and glossaries into your desired language.",
        )
        lang_map = {
            "English (Default)": "english",
            "हिंदी (Hindi)": "hindi",
            "ಕನ್ನಡ (Kannada)": "kannada",
        }
        language = lang_map.get(language_choice, "english")

        # Resolve Document A
        doc_a_text: Optional[str] = None
        doc_a_name: Optional[str] = None

        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            doc_a_name = uploaded_file.name
            sig = compute_file_signature(bytes_data, doc_a_name)

            if st.session_state.get("doc_a_sig") == sig and "doc_a_text" in st.session_state:
                doc_a_text = st.session_state["doc_a_text"]
            else:
                extracted, err = extract_text_from_file(bytes_data, doc_a_name)
                if err:
                    st.error(f"Error reading {doc_a_name}: {err}")
                else:
                    doc_a_text = extracted
                    st.session_state["doc_a_sig"] = sig
                    st.session_state["doc_a_text"] = doc_a_text
                    st.session_state["doc_a_name"] = doc_a_name

        elif sample_choice in sample_paths:
            f_path, f_name = sample_paths[sample_choice]
            doc_a_name = f_name
            try:
                with open(f_path, "r", encoding="utf-8") as f:
                    doc_a_text = f.read()
                st.session_state["doc_a_text"] = doc_a_text
                st.session_state["doc_a_name"] = doc_a_name
                st.session_state["doc_a_sig"] = f"sample_{sample_choice}"
            except OSError as exc:
                st.error(f"Failed to load sample: {exc}")

        # Resolve Document B
        doc_b_text: Optional[str] = None
        doc_b_name: Optional[str] = None

        if enable_compare:
            if uploaded_file_b is not None:
                b_bytes = uploaded_file_b.getvalue()
                doc_b_name = uploaded_file_b.name
                sig_b = compute_file_signature(b_bytes, doc_b_name)
                if st.session_state.get("doc_b_sig") == sig_b and "doc_b_text" in st.session_state:
                    doc_b_text = st.session_state["doc_b_text"]
                else:
                    extracted_b, err_b = extract_text_from_file(b_bytes, doc_b_name)
                    if err_b:
                        st.error(f"Error reading {doc_b_name}: {err_b}")
                    else:
                        doc_b_text = extracted_b
                        st.session_state["doc_b_sig"] = sig_b
                        st.session_state["doc_b_text"] = doc_b_text
                        st.session_state["doc_b_name"] = doc_b_name
            elif sample_choice == "Apex vs Horizon (Mutual NDA)":
                try:
                    with open("demo_data/sample_employment.txt", "r", encoding="utf-8") as f:
                        doc_b_text = f.read()
                    doc_b_name = "Zenith_Executive_Employment.txt"
                    st.session_state["doc_b_text"] = doc_b_text
                    st.session_state["doc_b_name"] = doc_b_name
                except OSError:
                    pass

        # 4. Document Telemetry HUD
        if doc_a_text:
            st.markdown(
                """
                <div style="margin-top: 20px; padding-top: 14px; border-top: 1px solid rgba(255, 255, 255, 0.06);">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #00f2fe; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">
                        Contract Telemetry
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            density = check_legal_density(doc_a_text)
            score = density["score"]
            score_color = "#10b981" if score >= 60 else ("#f59e0b" if score >= 25 else "#ef4444")

            st.markdown(
                f"""
                <div style="background: rgba(13, 20, 36, 0.75); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 14px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #94a3b8;">LEGAL DENSITY</span>
                        <span style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.1rem; color: {score_color};">{score}%</span>
                    </div>
                    <div style="width: 100%; height: 5px; background: rgba(255, 255, 255, 0.08); border-radius: 9999px; overflow: hidden;">
                        <div style="width: {score}%; height: 100%; background: {score_color}; border-radius: 9999px;"></div>
                    </div>
                    <div style="margin-top: 10px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #64748b;">
                        <div>CHARS: <span style="color: #cbd5e1;">{len(doc_a_text):,}</span></div>
                        <div>WORDS: <span style="color: #cbd5e1;">~{len(doc_a_text.split()):,}</span></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 5. Engine Telemetry Live Box
        call_info = get_last_call_info()
        source = call_info.get("source", "none")
        model = call_info.get("model_used", "none")
        duration = call_info.get("seconds", 0.0)

        if source != "none":
            status_color = "#00f2fe" if source == "live" else ("#10b981" if source == "cache" else "#fbbf24")
            st.markdown(
                f"""
                <div style="background: rgba(6, 10, 20, 0.85); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px; margin-top: 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="color: #64748b;">AI ROUTE:</span>
                        <span style="color: {status_color}; font-weight: 700; text-transform: uppercase;">● {source}</span>
                    </div>
                    <div style="color: #cbd5e1; word-break: break-all;">{model}</div>
                    <div style="color: #64748b; margin-top: 4px;">LATENCY: {duration:.2f}s</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 6. Session Reset
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        if st.button("↺ Reset Studio Session", use_container_width=True, help="Clear all caches and reset state."):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    return doc_a_text, doc_a_name, doc_b_text, doc_b_name, reading_level, language
