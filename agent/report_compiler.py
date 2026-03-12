"""
Report Compiler
===============
Utility functions for assembling and formatting the final report.
"""


def get_section_list(study) -> list[tuple[str, str, str]]:
    """
    Return a list of (tab_name, section_title, content) tuples
    for rendering in Streamlit tabs.
    """
    return [
        ("📋 Executive Summary", "Executive Industry Snapshot", study.executive_snapshot),
        ("📊 EBITDA Multiples", "EBITDA Multiples by Deal Size", study.ebitda_multiples),
        ("🗺️ Valuation Heat Map", "Valuation Heat Map", study.valuation_heatmap),
        ("⚡ Value Drivers", "Value Driver Sensitivity", study.value_drivers),
        ("🤝 Recent Transactions", "Recent Transaction Activity", study.recent_transactions),
        ("🎯 Ideal Buyers", "Ideal Buyer Universe", study.ideal_buyers),
        ("🔎 Secondary Buyers", "Secondary / Logical Buyers", study.secondary_buyers),
        ("📞 Buyer Strategy", "Buyer Targeting Strategy", study.buyer_targeting),
        ("💼 Deal Thesis", "Deal Thesis Summary", study.deal_thesis),
        ("⚠️ Risks", "Risks & Multiple Compression Factors", study.risks),
        ("🔬 Self-Critique", "Self-Critique", study.self_critique),
        ("📚 Sources", "Sources & Methodology", study.sources),
    ]
