"""
IFG Industry Market Study Agent
================================
AI-powered M&A market study generator for lower middle market industries.
Built for Iconic Founders Group.
"""

import re
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables (our API key lives in .env)
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="IFG Market Study Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap');

    /* Hide broken Material Icon text (keyboard_double_arrow) in sidebar toggle */
    [data-testid="stSidebarCollapsedControl"] span,
    button[kind="headerNoPadding"] span {
        font-size: 0 !important;
        overflow: hidden !important;
    }

    /* Global font — Times New Roman with web fallback */
    html, body, [class*="css"], .stMarkdown, .stMarkdown p, .stMarkdown li,
    .stMarkdown td, .stMarkdown th, .stTabs [data-baseweb="tab-panel"] {
        font-family: 'EB Garamond', 'Times New Roman', Times, serif !important;
    }

    /* Headers use a slightly different weight */
    h1, h2, h3, h4, .main-title {
        font-family: 'EB Garamond', 'Times New Roman', Times, serif !important;
    }

    /* Sidebar and UI elements stay sans-serif for clarity */
    [data-testid="stSidebar"], [data-testid="stSidebar"] * {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    .stButton button, .stSelectbox, .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    /* Main title */
    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #C9A84C;
        margin-bottom: 0;
        letter-spacing: 0.5px;
    }
    .subtitle {
        font-size: 1.15rem;
        color: #8892A0;
        margin-top: 4px;
        font-family: 'Inter', sans-serif !important;
        font-weight: 400;
    }

    /* Confidence badges — inline colored pills */
    .badge-high {
        background-color: #1B5E20;
        color: #fff;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.5px;
        white-space: nowrap;
        display: inline-block;
        vertical-align: middle;
        margin: 0 2px;
    }
    .badge-medium {
        background-color: #E65100;
        color: #fff;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.5px;
        white-space: nowrap;
        display: inline-block;
        vertical-align: middle;
        margin: 0 2px;
    }
    .badge-low {
        background-color: #B71C1C;
        color: #fff;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.5px;
        white-space: nowrap;
        display: inline-block;
        vertical-align: middle;
        margin: 0 2px;
    }

    /* Legend container */
    .confidence-legend {
        background-color: #161B22;
        border: 1px solid #2A2F3E;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 16px;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.8rem;
        color: #8892A0;
    }
    .confidence-legend strong {
        color: #C9A84C;
    }

    /* Section header gold underline */
    .section-header {
        border-bottom: 2px solid #C9A84C;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }

    /* Report body text sizing */
    .stMarkdown p { font-size: 1.05rem; line-height: 1.7; }
    .stMarkdown li { font-size: 1.0rem; line-height: 1.6; }

    /* Tables — cleaner IB look */
    .stMarkdown table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.92rem;
        margin: 12px 0;
    }
    .stMarkdown th {
        background-color: #1E2433;
        color: #C9A84C;
        font-weight: 600;
        padding: 10px 12px;
        text-align: left;
        border-bottom: 2px solid #C9A84C;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stMarkdown td {
        padding: 8px 12px;
        border-bottom: 1px solid #2A2F3E;
    }
    .stMarkdown tr:hover td {
        background-color: rgba(201, 168, 76, 0.05);
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        border-bottom: 2px solid #2A2F3E;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 2px solid #C9A84C !important;
        color: #C9A84C !important;
    }

    /* Download buttons */
    .stDownloadButton button {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600;
    }

    /* Heatmap color rows */
    .heatmap-table { width: 100%; border-collapse: collapse; margin: 12px 0; }
    .heatmap-table th {
        background-color: #1E2433; color: #C9A84C; font-weight: 600;
        padding: 10px 12px; text-align: left; border-bottom: 2px solid #C9A84C;
        font-family: 'Inter', sans-serif; font-size: 0.82rem;
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    .heatmap-table td {
        padding: 10px 12px; border-bottom: 1px solid #2A2F3E;
        font-family: 'EB Garamond', 'Times New Roman', serif; font-size: 0.95rem;
    }
    .heatmap-tier-1 td { background-color: rgba(183, 28, 28, 0.18); }
    .heatmap-tier-2 td { background-color: rgba(230, 81, 0, 0.15); }
    .heatmap-tier-3 td { background-color: rgba(201, 168, 76, 0.15); }
    .heatmap-tier-4 td { background-color: rgba(27, 94, 32, 0.20); }
    .heatmap-tier-1 td:first-child { border-left: 4px solid #B71C1C; font-weight: 700; color: #EF9A9A; }
    .heatmap-tier-2 td:first-child { border-left: 4px solid #E65100; font-weight: 700; color: #FFCC80; }
    .heatmap-tier-3 td:first-child { border-left: 4px solid #C9A84C; font-weight: 700; color: #C9A84C; }
    .heatmap-tier-4 td:first-child { border-left: 4px solid #1B5E20; font-weight: 700; color: #A5D6A7; }
</style>
""", unsafe_allow_html=True)


def convert_confidence_tags(text: str) -> str:
    """
    Replace [HIGH CONFIDENCE], [MEDIUM CONFIDENCE], [LOW CONFIDENCE] text tags
    with colored HTML badge spans.
    """
    if not text:
        return text
    text = re.sub(
        r'\[HIGH CONFIDENCE\]',
        '<span class="badge-high">HIGH</span>',
        text
    )
    text = re.sub(
        r'\[MEDIUM CONFIDENCE\]',
        '<span class="badge-medium">MEDIUM</span>',
        text
    )
    text = re.sub(
        r'\[LOW CONFIDENCE\]',
        '<span class="badge-low">LOW</span>',
        text
    )
    return text


def apply_heatmap_colors(text: str) -> str:
    """
    Convert the Valuation Heat Map markdown table into a color-coded HTML table.
    Rows are colored by tier: 4x (red), 5.5x (orange), 7x (gold), 8.5x+ (green).
    """
    lines = text.split('\n')
    result_lines = []
    in_table = False
    header_done = False
    row_index = 0

    tier_colors = [
        'heatmap-tier-1',  # 4.0x-5.5x — red
        'heatmap-tier-2',  # 5.5x-7.0x — orange
        'heatmap-tier-3',  # 7.0x-8.5x — gold
        'heatmap-tier-4',  # 8.5x+     — green
    ]

    for line in lines:
        stripped = line.strip()

        # Detect table start
        if stripped.startswith('|') and not in_table:
            in_table = True
            header_done = False
            row_index = 0
            # Parse header
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            header_html = ''.join(f'<th>{c}</th>' for c in cells)
            result_lines.append('<table class="heatmap-table">')
            result_lines.append(f'<tr>{header_html}</tr>')
            continue

        # Skip separator row (|---|---|)
        if in_table and re.match(r'^\|[\s\-:|]+\|$', stripped):
            header_done = True
            continue

        # Data rows
        if in_table and stripped.startswith('|') and header_done:
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            tier_class = tier_colors[row_index] if row_index < len(tier_colors) else tier_colors[-1]
            cells_html = ''.join(f'<td>{c}</td>' for c in cells)
            result_lines.append(f'<tr class="{tier_class}">{cells_html}</tr>')
            row_index += 1
            continue

        # End of table
        if in_table and not stripped.startswith('|'):
            in_table = False
            result_lines.append('</table>')
            result_lines.append(line)
            continue

        result_lines.append(line)

    # Close table if text ends inside one
    if in_table:
        result_lines.append('</table>')

    return '\n'.join(result_lines)


# --- Header ---
st.markdown('<p class="main-title">Industry Market Study Agent</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Iconic Founders Group  |  Lower Middle Market M&A Advisory</p>', unsafe_allow_html=True)
st.markdown("---")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("Report Configuration")

    industry = st.selectbox(
        "Select Industry",
        [
            "HVAC",
            "Commercial Landscaping",
            "Pest Control",
            "Roofing",
            "Environmental Remediation",
            "Wastewater Services",
            "Industrial Services"
        ],
        help="Choose the industry to generate an M&A market study for."
    )

    st.markdown("---")

    st.info(
        "This agent generates an IB-quality market study including "
        "EBITDA multiples, value drivers, recent transactions, buyer "
        "profiles, and strategic recommendations — all with source citations."
    )

    st.markdown("---")

    # Confidence legend in sidebar
    st.markdown("""
    <div class="confidence-legend">
        <strong>Confidence Scoring</strong><br><br>
        <span class="badge-high">HIGH</span> Published source with verifiable URL<br><br>
        <span class="badge-medium">MEDIUM</span> Web search, proxy data, or industry estimate<br><br>
        <span class="badge-low">LOW</span> Directional commentary; limited public data
    </div>
    """, unsafe_allow_html=True)

    st.caption("Powered by Google Gemini 2.5 Flash")
    st.caption("Data: Public sources + curated knowledge base")

# --- Main Content Area ---

generate_clicked = st.button(
    "🔍 Generate Market Study",
    type="primary",
    use_container_width=True
)

if generate_clicked:
    from agent.pipeline import generate_market_study
    from agent.report_compiler import get_section_list

    with st.status("Generating market study...", expanded=True) as status:
        def progress_callback(step: int, step_name: str, total: int):
            st.write(f"**Step {step}/{total}:** {step_name}")

        try:
            study = generate_market_study(industry, progress_callback=progress_callback)
            status.update(label="✅ Report generated!", state="complete")
        except Exception as e:
            status.update(label="❌ Generation failed", state="error")
            st.error(f"An error occurred: {str(e)}")
            st.stop()

    st.session_state["study"] = study
    st.session_state["study_industry"] = industry

# --- Render Report ---
if "study" in st.session_state:
    study = st.session_state["study"]
    study_industry = st.session_state["study_industry"]

    from agent.report_compiler import get_section_list

    section_list = get_section_list(study)

    # Build tabs
    tab_names = [s[0] for s in section_list]
    tabs = st.tabs(tab_names)

    for i, (tab_name, section_title, content) in enumerate(section_list):
        with tabs[i]:
            st.markdown(f"## {section_title}: {study_industry}")
            if content:
                # Strip duplicate section headers that Gemini or templates may include
                cleaned = re.sub(r'^##\s+.*?\n', '', content, count=1).strip()
                # Convert [HIGH CONFIDENCE] etc. into colored badges
                styled_content = convert_confidence_tags(cleaned)
                # Apply heatmap coloring for the Valuation Heat Map tab
                if "Valuation Heat Map" in section_title:
                    styled_content = apply_heatmap_colors(styled_content)
                st.markdown(styled_content, unsafe_allow_html=True)
            else:
                st.warning("This section could not be generated.")

    # --- Download Section ---
    st.markdown("---")

    full_md = study.full_report_markdown()

    # Generate PDF
    from report.pdf_generator import generate_pdf
    try:
        pdf_bytes = generate_pdf(study)
        pdf_ready = True
    except Exception as e:
        pdf_bytes = b""
        pdf_ready = False
        st.warning(f"PDF generation failed: {str(e)}")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download as Markdown",
            data=full_md,
            file_name=f"{study_industry.lower().replace(' ', '_')}_market_study.md",
            mime="text/markdown",
        )
    with col2:
        st.download_button(
            label="📥 Download as PDF",
            data=pdf_bytes if pdf_ready else b"",
            file_name=f"{study_industry.lower().replace(' ', '_')}_market_study.pdf",
            mime="application/pdf",
            disabled=not pdf_ready,
        )

else:
    # Landing page
    st.markdown("")
    st.markdown("### How It Works")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 1. Select Industry")
        st.markdown("Choose from 7 blue-collar industries that IFG advises on.")

    with col2:
        st.markdown("#### 2. Generate Study")
        st.markdown(
            "AI researches EBITDA multiples, recent transactions, and active buyers in real-time "
            "using Google Search and a curated knowledge base."
        )

    with col3:
        st.markdown("#### 3. Download Report")
        st.markdown(
            "Get an IB-quality market study with source citations, "
            "confidence scoring, and PDF export."
        )

    st.markdown("---")

    # Report sections as styled cards grid
    st.markdown("""
    <div style="
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin: 8px 0 16px 0;
    ">
        <div style="background:#161B22;border:1px solid #2A2F3E;border-radius:6px;padding:14px 12px;text-align:center;">
            <div style="font-size:1.3rem;margin-bottom:4px;">📋</div>
            <div style="color:#C9A84C;font-weight:600;font-size:0.82rem;font-family:Inter,sans-serif;">Executive Snapshot</div>
        </div>
        <div style="background:#161B22;border:1px solid #2A2F3E;border-radius:6px;padding:14px 12px;text-align:center;">
            <div style="font-size:1.3rem;margin-bottom:4px;">📊</div>
            <div style="color:#C9A84C;font-weight:600;font-size:0.82rem;font-family:Inter,sans-serif;">EBITDA Multiples</div>
        </div>
        <div style="background:#161B22;border:1px solid #2A2F3E;border-radius:6px;padding:14px 12px;text-align:center;">
            <div style="font-size:1.3rem;margin-bottom:4px;">🗺️</div>
            <div style="color:#C9A84C;font-weight:600;font-size:0.82rem;font-family:Inter,sans-serif;">Valuation Heat Map</div>
        </div>
        <div style="background:#161B22;border:1px solid #2A2F3E;border-radius:6px;padding:14px 12px;text-align:center;">
            <div style="font-size:1.3rem;margin-bottom:4px;">⚡</div>
            <div style="color:#C9A84C;font-weight:600;font-size:0.82rem;font-family:Inter,sans-serif;">Value Drivers</div>
        </div>
        <div style="background:#161B22;border:1px solid #2A2F3E;border-radius:6px;padding:14px 12px;text-align:center;">
            <div style="font-size:1.3rem;margin-bottom:4px;">🤝</div>
            <div style="color:#C9A84C;font-weight:600;font-size:0.82rem;font-family:Inter,sans-serif;">Recent Transactions</div>
        </div>
        <div style="background:#161B22;border:1px solid #2A2F3E;border-radius:6px;padding:14px 12px;text-align:center;">
            <div style="font-size:1.3rem;margin-bottom:4px;">🎯</div>
            <div style="color:#C9A84C;font-weight:600;font-size:0.82rem;font-family:Inter,sans-serif;">Ideal Buyers</div>
        </div>
        <div style="background:#161B22;border:1px solid #2A2F3E;border-radius:6px;padding:14px 12px;text-align:center;">
            <div style="font-size:1.3rem;margin-bottom:4px;">🔎</div>
            <div style="color:#C9A84C;font-weight:600;font-size:0.82rem;font-family:Inter,sans-serif;">Secondary Buyers</div>
        </div>
        <div style="background:#161B22;border:1px solid #2A2F3E;border-radius:6px;padding:14px 12px;text-align:center;">
            <div style="font-size:1.3rem;margin-bottom:4px;">📞</div>
            <div style="color:#C9A84C;font-weight:600;font-size:0.82rem;font-family:Inter,sans-serif;">Buyer Strategy</div>
        </div>
        <div style="background:#161B22;border:1px solid #2A2F3E;border-radius:6px;padding:14px 12px;text-align:center;">
            <div style="font-size:1.3rem;margin-bottom:4px;">💼</div>
            <div style="color:#C9A84C;font-weight:600;font-size:0.82rem;font-family:Inter,sans-serif;">Deal Thesis</div>
        </div>
        <div style="background:#161B22;border:1px solid #2A2F3E;border-radius:6px;padding:14px 12px;text-align:center;">
            <div style="font-size:1.3rem;margin-bottom:4px;">⚠️</div>
            <div style="color:#C9A84C;font-weight:600;font-size:0.82rem;font-family:Inter,sans-serif;">Risk Analysis</div>
        </div>
        <div style="background:#161B22;border:1px solid #2A2F3E;border-radius:6px;padding:14px 12px;text-align:center;">
            <div style="font-size:1.3rem;margin-bottom:4px;">🔬</div>
            <div style="color:#C9A84C;font-weight:600;font-size:0.82rem;font-family:Inter,sans-serif;">Self-Critique</div>
        </div>
        <div style="background:#161B22;border:1px solid #2A2F3E;border-radius:6px;padding:14px 12px;text-align:center;">
            <div style="font-size:1.3rem;margin-bottom:4px;">📚</div>
            <div style="color:#C9A84C;font-weight:600;font-size:0.82rem;font-family:Inter,sans-serif;">Sources</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
