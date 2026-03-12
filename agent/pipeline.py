"""
Agent Pipeline
==============
The main orchestration function: generate_market_study()

This is the "conductor" — it coordinates all the tools and prompts
to produce a complete market study. Here's the flow:

1. Load knowledge base (our pre-saved data)
2. For each section: combine KB data + web search → send to Gemini → get text
3. Run a self-critique pass at the end
4. Package everything into a structured report

Teaching note: This uses a "prompt chain" architecture — each section
is generated independently with its own tailored prompt. This is simpler
and more reliable than a complex multi-agent system.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from agent.tools import (
    load_knowledge_base,
    load_buyers_data,
    format_kb_for_prompt,
    generate_section,
    generate_section_with_search,
)
from agent.prompts import (
    EXECUTIVE_SNAPSHOT_PROMPT,
    EBITDA_MULTIPLES_PROMPT,
    VALUATION_HEATMAP_PROMPT,
    VALUE_DRIVERS_PROMPT,
    RECENT_TRANSACTIONS_PROMPT,
    IDEAL_BUYERS_PROMPT,
    SECONDARY_BUYERS_PROMPT,
    BUYER_TARGETING_PROMPT,
    DEAL_THESIS_PROMPT,
    RISKS_PROMPT,
    SELF_CRITIQUE_PROMPT,
    SOURCES_TEMPLATE,
)


@dataclass
class MarketStudy:
    """
    Holds all sections of a completed market study.

    Teaching note: A dataclass is like a simple container.
    Instead of passing around a dictionary, we define exactly what
    fields a market study has. This makes the code self-documenting.
    """
    industry: str
    generated_at: str = ""
    executive_snapshot: str = ""
    ebitda_multiples: str = ""
    valuation_heatmap: str = ""
    value_drivers: str = ""
    recent_transactions: str = ""
    ideal_buyers: str = ""
    secondary_buyers: str = ""
    buyer_targeting: str = ""
    deal_thesis: str = ""
    risks: str = ""
    self_critique: str = ""
    sources: str = ""
    all_sources: list = field(default_factory=list)

    def full_report_markdown(self) -> str:
        """Combine all sections into one big Markdown document."""
        sections = [
            f"# {self.industry} M&A Market Study",
            f"**Prepared by Iconic Founders Group** | {self.generated_at}",
            "---",
            "## 1. Executive Industry Snapshot",
            self.executive_snapshot,
            "---",
            "## 2. EBITDA Multiples by Deal Size",
            self.ebitda_multiples,
            "---",
            "## 3. Valuation Heat Map",
            self.valuation_heatmap,
            "---",
            "## 4. Value Driver Sensitivity",
            self.value_drivers,
            "---",
            "## 5. Recent Transaction Activity",
            self.recent_transactions,
            "---",
            "## 6. Ideal Buyer Universe",
            self.ideal_buyers,
            "---",
            "## 7. Secondary / Logical Buyers",
            self.secondary_buyers,
            "---",
            "## 8. Buyer Targeting Strategy",
            self.buyer_targeting,
            "---",
            "## 9. Deal Thesis Summary",
            self.deal_thesis,
            "---",
            "## 10. Risks & Multiple Compression Factors",
            self.risks,
            "---",
            "## 11. Self-Critique",
            self.self_critique,
            "---",
            "## 12. Sources & Methodology",
            self.sources,
        ]
        return "\n\n".join(sections)


def generate_market_study(industry: str, progress_callback=None) -> MarketStudy:
    """
    Generate a complete market study for the given industry.

    This is the main function — it runs through all 12 sections sequentially.

    Args:
        industry: e.g. "HVAC" or "Commercial Landscaping"
        progress_callback: Optional function to report progress (used by Streamlit)
                          Called with (step_number, step_name, total_steps)

    Returns:
        A MarketStudy object with all sections filled in
    """

    study = MarketStudy(
        industry=industry,
        generated_at=datetime.now().strftime("%B %d, %Y"),
    )

    total_steps = 12

    def update_progress(step: int, name: str):
        """Helper to report progress if a callback is provided."""
        if progress_callback:
            progress_callback(step, name, total_steps)

    # =========================================================================
    # Step 0: Load the knowledge base
    # =========================================================================
    update_progress(0, "Loading industry knowledge base...")
    kb_data = load_knowledge_base(industry)
    buyers_data = load_buyers_data()

    # Format KB data for different sections
    kb_all = format_kb_for_prompt(kb_data, "all")
    kb_multiples = format_kb_for_prompt(kb_data, "multiples")
    kb_value_drivers = format_kb_for_prompt(kb_data, "value_drivers")
    kb_transactions = format_kb_for_prompt(kb_data, "transactions")
    kb_buyers = format_kb_for_prompt(kb_data, "buyers")

    # Add cross-industry buyer data
    if buyers_data:
        kb_buyers += "\n\n=== CROSS-INDUSTRY PE FIRMS ===\n"
        import json
        kb_buyers += json.dumps(buyers_data, indent=2)

    # =========================================================================
    # Step 1: Executive Industry Snapshot
    # Uses web search for fresh market data + KB for baseline
    # =========================================================================
    update_progress(1, "Researching industry landscape...")
    study.executive_snapshot = generate_section_with_search(
        prompt=EXECUTIVE_SNAPSHOT_PROMPT,
        search_queries=[
            f"{industry} industry market size growth 2025",
            f"{industry} private equity M&A activity 2024 2025",
        ],
        kb_context=format_kb_for_prompt(kb_data, "overview"),
        industry=industry,
    )

    # =========================================================================
    # Step 2: EBITDA Multiples
    # KB is primary (our curated data), web search for latest trends
    # =========================================================================
    update_progress(2, "Analyzing EBITDA multiples...")
    study.ebitda_multiples = generate_section_with_search(
        prompt=EBITDA_MULTIPLES_PROMPT,
        search_queries=[
            f"{industry} EBITDA multiples lower middle market 2025",
        ],
        kb_context=kb_multiples,
        industry=industry,
    )

    # =========================================================================
    # Step 3: Valuation Heat Map
    # Generated from multiples data + value drivers (no web search needed)
    # =========================================================================
    update_progress(3, "Building valuation heat map...")
    heatmap_context = kb_multiples + "\n\n" + kb_value_drivers
    study.valuation_heatmap = generate_section(
        prompt=VALUATION_HEATMAP_PROMPT,
        context=heatmap_context,
        industry=industry,
    )

    # =========================================================================
    # Step 4: Value Driver Sensitivity
    # KB provides the drivers, LLM adds IB-quality analysis
    # =========================================================================
    update_progress(4, "Analyzing value drivers...")
    study.value_drivers = generate_section(
        prompt=VALUE_DRIVERS_PROMPT,
        context=kb_value_drivers,
        industry=industry,
    )

    # =========================================================================
    # Step 5: Recent Transactions
    # Web search is critical here for fresh deal data
    # =========================================================================
    update_progress(5, "Searching for recent transactions...")
    study.recent_transactions = generate_section_with_search(
        prompt=RECENT_TRANSACTIONS_PROMPT,
        search_queries=[
            f"{industry} company acquisition deal 2024 2025",
            f"{industry} M&A transaction private equity 2024",
        ],
        kb_context=kb_transactions,
        industry=industry,
    )

    # =========================================================================
    # Step 6: Ideal Buyer Universe
    # KB provides known buyers, web search for latest activity
    # =========================================================================
    update_progress(6, "Profiling ideal buyers...")
    study.ideal_buyers = generate_section_with_search(
        prompt=IDEAL_BUYERS_PROMPT,
        search_queries=[
            f"private equity firms investing in {industry} companies 2024 2025",
        ],
        kb_context=kb_buyers,
        industry=industry,
    )

    # =========================================================================
    # Step 7: Secondary / Logical Buyers
    # =========================================================================
    update_progress(7, "Identifying secondary buyers...")
    study.secondary_buyers = generate_section(
        prompt=SECONDARY_BUYERS_PROMPT,
        context=kb_buyers,
        industry=industry,
    )

    # =========================================================================
    # Step 8: Buyer Targeting Strategy
    # Pure LLM analysis based on buyer data generated above
    # =========================================================================
    update_progress(8, "Developing buyer targeting strategy...")
    targeting_context = (
        f"=== IDEAL BUYERS ===\n{study.ideal_buyers}\n\n"
        f"=== SECONDARY BUYERS ===\n{study.secondary_buyers}"
    )
    study.buyer_targeting = generate_section(
        prompt=BUYER_TARGETING_PROMPT,
        context=targeting_context,
        industry=industry,
    )

    # =========================================================================
    # Step 9: Deal Thesis Summary
    # Synthesizes ALL data into a pitch-book-style thesis
    # =========================================================================
    update_progress(9, "Crafting deal thesis...")
    thesis_context = (
        f"=== EXECUTIVE SNAPSHOT ===\n{study.executive_snapshot}\n\n"
        f"=== MULTIPLES ===\n{study.ebitda_multiples}\n\n"
        f"=== BUYER DEMAND ===\n{study.ideal_buyers[:1000]}"
    )
    study.deal_thesis = generate_section(
        prompt=DEAL_THESIS_PROMPT,
        context=thesis_context,
        industry=industry,
    )

    # =========================================================================
    # Step 10: Risks & Multiple Compression
    # =========================================================================
    update_progress(10, "Assessing risks...")
    study.risks = generate_section_with_search(
        prompt=RISKS_PROMPT,
        search_queries=[
            f"{industry} industry risks challenges 2025 tariffs labor",
        ],
        kb_context=kb_all,
        industry=industry,
    )

    # =========================================================================
    # Step 11: Self-Critique
    # The AI critiques its OWN report — the killer differentiator
    # =========================================================================
    update_progress(11, "Running self-critique...")
    # Feed the full report so far into the critique prompt
    # Self-critique is special — it uses {report_content} not {industry}/{context}
    full_report_so_far = study.full_report_markdown()

    from agent.prompts import MASTER_SYSTEM_PROMPT
    from agent.tools import client, MODEL
    from google.genai import types as genai_types

    try:
        critique_prompt = SELF_CRITIQUE_PROMPT.format(
            report_content=full_report_so_far[:8000]  # Truncate to fit context
        )
        response = client.models.generate_content(
            model=MODEL,
            contents=critique_prompt,
            config=genai_types.GenerateContentConfig(
                system_instruction=MASTER_SYSTEM_PROMPT,
            ),
        )
        study.self_critique = response.text if response.text else "*No critique generated.*"
    except Exception as e:
        study.self_critique = f"*Self-critique generation failed: {str(e)}*"

    # =========================================================================
    # Step 12: Sources & Methodology
    # Compile all source URLs mentioned throughout the report
    # =========================================================================
    update_progress(12, "Compiling sources...")

    # Collect source URLs from the knowledge base
    source_list = []
    if kb_data:
        # From multiples
        for bracket, data in kb_data.get("ebitda_multiples", {}).items():
            if "source_url" in data:
                source_list.append(f"- [{data.get('source', 'Source')}]({data['source_url']})")
        # From transactions
        for txn in kb_data.get("recent_transactions", []):
            if "source_url" in txn:
                source_list.append(f"- [{txn.get('source', 'Source')}]({txn['source_url']})")
        # From buyers
        for buyer_type in ["pe_platforms", "strategic"]:
            for buyer in kb_data.get("known_buyers", {}).get(buyer_type, []):
                if "source_url" in buyer:
                    source_list.append(f"- [{buyer.get('name', 'Source')}]({buyer['source_url']})")

    # Deduplicate sources
    source_list = list(dict.fromkeys(source_list))

    study.sources = SOURCES_TEMPLATE.format(
        sources_list="\n".join(source_list) if source_list else "- Sources cited inline throughout the report",
        date=study.generated_at,
    )

    return study
