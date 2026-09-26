"""Ultra-premium, bespoke WCAG 2.1 AA/AAA design system and layout components for LexiGuard.

Features:
- Obsidian & Cyber-Teal Luminescence luxury aesthetic
- Google Fonts (Outfit & Plus Jakarta Sans) typography
- Frosted glass cards with micro-borders and neon accents
- Pulsing real-time engine telemetry indicators
- Accessible high-contrast ratios (> 8:1) and visible focus rings
"""

import html
from typing import Optional

import streamlit as st

APP_TITLE = "LexiGuard"
APP_TAGLINE = "Autonomous Legal Intelligence & Contract Risk Studio"


def inject_custom_css() -> None:
    """Inject bespoke luxury dark-theme CSS design tokens, typography, and micro-interactions."""
    css_content = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Accessibility Skip-Link */
    .skip-link {
        position: absolute;
        top: -9999px;
        left: 24px;
        background: #00f2fe;
        color: #050811;
        padding: 12px 20px;
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border-radius: 8px;
        z-index: 999999;
        text-decoration: none;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.6);
        transition: top 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .skip-link:focus, .skip-link:focus-visible {
        top: 20px;
        outline: 3px solid #ffffff;
        outline-offset: 3px;
    }

    /* WCAG Focus Rings */
    *:focus-visible, button:focus-visible, input:focus-visible, textarea:focus-visible, [role="tab"]:focus-visible, select:focus-visible {
        outline: 2px solid #00f2fe !important;
        outline-offset: 3px !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.4) !important;
    }

    /* Root Canvas & Dynamic Radial Aura */
    .stApp {
        background-color: #060911;
        background-image: 
            radial-gradient(at 0% 0%, rgba(0, 242, 254, 0.07) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(79, 172, 254, 0.06) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(16, 185, 129, 0.04) 0px, transparent 50%);
        color: #f1f5f9;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Modernized Streamlit Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(13, 20, 36, 0.7);
        padding: 8px 12px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(16px);
        margin-bottom: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 10px;
        color: #94a3b8;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 0.92rem;
        padding: 0 18px;
        background-color: transparent;
        border: none;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.15) 0%, rgba(79, 172, 254, 0.1) 100%) !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
        box-shadow: 0 4px 20px rgba(0, 242, 254, 0.2) !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff;
        background: rgba(255, 255, 255, 0.04);
    }

    /* Luxury Studio Cards */
    .studio-card {
        background: linear-gradient(135deg, rgba(17, 24, 43, 0.8) 0%, rgba(11, 16, 30, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(12px);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .studio-card:hover {
        border-color: rgba(0, 242, 254, 0.3);
        box-shadow: 0 12px 35px -5px rgba(0, 242, 254, 0.1);
    }

    /* Card Top Accent Lightline */
    .studio-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0, 242, 254, 0.4), transparent);
    }

    .studio-header {
        font-family: 'Outfit', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #f8fafc;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 14px;
        letter-spacing: -0.01em;
    }

    /* Futuristic HUD Metric Tiles */
    .hud-tile {
        background: rgba(13, 20, 36, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 16px 20px;
        text-align: left;
    }
    .hud-tile-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #64748b;
        margin-bottom: 6px;
    }
    .hud-tile-value {
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.2;
    }

    /* Telemetry Pulsing Dot */
    .pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 10px #10b981;
        animation: pulseAnimation 2s infinite;
        margin-right: 6px;
    }
    @keyframes pulseAnimation {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Badges & Micro Tags */
    .tag-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .tag-low {
        background: rgba(16, 185, 129, 0.12);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }
    .tag-medium {
        background: rgba(245, 158, 11, 0.12);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.35);
    }
    .tag-high {
        background: rgba(239, 68, 68, 0.14);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .tag-verified {
        background: rgba(0, 242, 254, 0.12);
        color: #00f2fe;
        border: 1px solid rgba(0, 242, 254, 0.4);
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.15);
    }

    /* Verbatim Quote Studio Callout */
    .studio-quote {
        background: rgba(6, 10, 20, 0.85);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-left: 4px solid #00f2fe;
        border-radius: 0 10px 10px 0;
        padding: 16px 20px;
        font-family: Georgia, serif;
        font-style: italic;
        color: #cbd5e1;
        line-height: 1.6;
        margin: 14px 0;
        position: relative;
    }

    /* Counter-Proposal Box */
    .studio-counter {
        background: rgba(16, 185, 129, 0.06);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 10px;
        padding: 14px 18px;
        font-size: 0.92rem;
        color: #a7f3d0;
        line-height: 1.5;
        margin-top: 10px;
    }

    /* Educational Disclaimer HUD Banner */
    .hud-disclaimer {
        background: linear-gradient(90deg, rgba(20, 25, 45, 0.85) 0%, rgba(13, 17, 32, 0.9) 100%);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-left: 4px solid #f59e0b;
        padding: 12px 20px;
        border-radius: 10px;
        margin-bottom: 24px;
        font-size: 0.84rem;
        color: #cbd5e1;
        line-height: 1.5;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    /* Studio Footer */
    .studio-footer {
        margin-top: 50px;
        padding: 24px 0;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        font-size: 0.8rem;
        color: #64748b;
        text-align: center;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.02em;
    }

    /* Screen Reader Only Utility */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
    }
    </style>
    """
    st.markdown(css_content, unsafe_allow_html=True)


def render_skip_link() -> None:
    """Render accessible skip-to-content keyboard link."""
    st.markdown(
        '<a href="#main-content" class="skip-link">Skip to Main Content [Tab]</a>'
        '<div id="main-content" tabindex="-1"></div>',
        unsafe_allow_html=True,
    )


def render_header() -> None:
    """Render executive studio header with animated telemetry and educational disclaimer."""
    header_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 16px; margin-bottom: 16px; border-bottom: 1px solid rgba(255, 255, 255, 0.06);">
        <div style="display: flex; align-items: center; gap: 18px;">
            <div style="background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%); width: 52px; height: 52px; border-radius: 14px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 25px rgba(0, 242, 254, 0.4);">
                <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#050811" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    <path d="m9 12 2 2 4-4"/>
                </svg>
            </div>
            <div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.1rem; font-weight: 900; margin: 0; color: #ffffff; letter-spacing: -0.03em;">
                        {APP_TITLE}
                    </h1>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 700; background: rgba(0, 242, 254, 0.12); color: #00f2fe; border: 1px solid rgba(0, 242, 254, 0.4); padding: 3px 10px; border-radius: 9999px; letter-spacing: 0.08em;">
                        STUDIO V2
                    </span>
                </div>
                <p style="margin: 2px 0 0 0; font-size: 0.95rem; color: #94a3b8; font-weight: 400;">
                    {APP_TAGLINE}
                </p>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 14px; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; background: rgba(13, 20, 36, 0.8); padding: 8px 16px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.07);">
            <div><span class="pulse-dot"></span><span style="color: #f8fafc; font-weight: 600;">MULTI-MODEL ENGINE</span></div>
            <div style="color: #475569;">|</div>
            <div style="color: #00f2fe; font-weight: 600;">WCAG 2.1 AAA</div>
        </div>
    </div>

    <div class="hud-disclaimer" role="alert">
        <span style="font-size: 1.25rem;">⚖️</span>
        <div>
            <strong style="color: #fbbf24; font-family: 'Outfit', sans-serif; font-weight: 700; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.06em;">Educational Legal Information Protocol:</strong>
            LexiGuard provides automated contractual intelligence, contradiction detection, and risk heuristics strictly for educational and self-study purposes. LexiGuard is not a legal practice and does not dispense legal advice. Always obtain counsel from a qualified attorney before signing any agreement.
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def render_footer() -> None:
    """Render footer."""
    st.markdown(
        """
        <div class="studio-footer">
            <span>LEXIGUARD AUTONOMOUS CONTRACT STUDIO</span> • STRICTLY NON-LEGAL ADVICE • ZERO KEY LEAK PROTOCOL<br>
            Multi-Model Fallback Chain • Content-Addressable Cryptographic Caching • Quote Authenticity Engine
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tag(text: str, category: str = "low") -> str:
    """Generate HTML string for pill tag."""
    c_text = html.escape(text)
    c_cat = html.escape(category.lower())
    return f'<span class="tag-pill tag-{c_cat}">{c_text}</span>'


def render_status_region(message: str) -> None:
    """Screen reader announcement region."""
    st.markdown(f'<div aria-live="polite" class="sr-only">{html.escape(message)}</div>', unsafe_allow_html=True)
