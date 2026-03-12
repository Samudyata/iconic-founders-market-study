"""
Agent Tools
===========
These are the "hands" of the agent — functions that fetch data and call the AI.

Three main tools:
1. load_knowledge_base() — reads our pre-saved industry data from JSON files
2. web_search() — asks Gemini to search the web for current data (with citations)
3. generate_section() — sends a prompt + context to Gemini and gets back text

Uses the new `google-genai` SDK (replaces deprecated `google-generativeai`).
"""

import json
import os
import time
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# --- Configure Gemini Client ---
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Model to use — gemini-2.5-flash is free tier and supports Google Search grounding
MODEL = "gemini-2.5-flash"

# The base directory where our data files live
DATA_DIR = Path(__file__).parent.parent / "data"

# Map friendly names to JSON file names
INDUSTRY_MAP = {
    "HVAC": "hvac",
    "Commercial Landscaping": "landscaping",
    "Pest Control": "pest_control",
    "Roofing": "roofing",
    "Environmental Remediation": "remediation",
    "Wastewater Services": "wastewater",
    "Industrial Services": "industrial_services",
}


def load_knowledge_base(industry: str) -> dict:
    """
    Load the curated knowledge base for a given industry.

    This reads the JSON file we pre-built with real data (multiples, buyers, etc.)
    Think of it as: opening your research notebook to the right page.

    Args:
        industry: e.g. "HVAC" or "Commercial Landscaping"

    Returns:
        Dictionary with all the pre-researched data, or empty dict if file missing
    """
    file_key = INDUSTRY_MAP.get(industry, industry.lower().replace(" ", "_"))
    file_path = DATA_DIR / "industries" / f"{file_key}.json"

    if not file_path.exists():
        print(f"Warning: No knowledge base found for {industry} at {file_path}")
        return {}

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def load_buyers_data() -> dict:
    """Load the cross-industry PE firms and strategic buyers data."""
    buyers = {}
    for filename in ["pe_firms.json", "strategic_buyers.json"]:
        filepath = DATA_DIR / "buyers" / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                buyers[filename.replace(".json", "")] = json.load(f)
    return buyers


def format_kb_for_prompt(kb_data: dict, section: str = "all") -> str:
    """
    Convert knowledge base data into a readable string for the LLM prompt.

    Args:
        kb_data: The dictionary from load_knowledge_base()
        section: Which part to format ("multiples", "value_drivers", "transactions",
                 "buyers", "overview", or "all")

    Returns:
        A formatted string ready to paste into a prompt
    """
    if not kb_data:
        return "No curated knowledge base data available for this industry."

    parts = []

    if section in ("all", "overview"):
        if "overview" in kb_data:
            parts.append("=== INDUSTRY OVERVIEW ===")
            overview = kb_data["overview"]
            for key, value in overview.items():
                parts.append(f"- {key}: {value}")

    if section in ("all", "multiples"):
        if "ebitda_multiples" in kb_data:
            parts.append("\n=== EBITDA MULTIPLES (from curated knowledge base) ===")
            for bracket, data in kb_data["ebitda_multiples"].items():
                parts.append(f"\nDeal Size: {bracket}")
                for key, value in data.items():
                    parts.append(f"  {key}: {value}")

    if section in ("all", "value_drivers"):
        if "value_drivers" in kb_data:
            parts.append("\n=== VALUE DRIVERS ===")
            for driver in kb_data["value_drivers"]:
                parts.append(f"\n- Factor: {driver.get('factor', 'N/A')}")
                parts.append(f"  Impact: {driver.get('impact', 'N/A')}")
                parts.append(f"  Detail: {driver.get('explanation', 'N/A')}")
                if "source" in driver:
                    parts.append(f"  Source: {driver['source']}")

    if section in ("all", "transactions"):
        if "recent_transactions" in kb_data:
            parts.append("\n=== RECENT TRANSACTIONS ===")
            for txn in kb_data["recent_transactions"]:
                parts.append(f"\n- Date: {txn.get('date', 'N/A')}")
                parts.append(f"  Target: {txn.get('target', 'N/A')}")
                parts.append(f"  Acquirer: {txn.get('acquirer', 'N/A')}")
                parts.append(f"  Type: {txn.get('type', 'N/A')}")
                parts.append(f"  Deal Size: {txn.get('deal_size', 'Undisclosed')}")
                parts.append(f"  Source: {txn.get('source', 'N/A')}")
                if "source_url" in txn:
                    parts.append(f"  Source URL: {txn['source_url']}")

    if section in ("all", "buyers"):
        if "known_buyers" in kb_data:
            parts.append("\n=== KNOWN BUYERS ===")
            buyers = kb_data["known_buyers"]
            if "pe_platforms" in buyers:
                parts.append("\nPrivate Equity Platforms:")
                for buyer in buyers["pe_platforms"]:
                    parts.append(f"\n  - Name: {buyer.get('name', 'N/A')}")
                    parts.append(f"    Platform: {buyer.get('platform', 'N/A')}")
                    parts.append(f"    Thesis: {buyer.get('thesis', 'N/A')}")
                    if "source_url" in buyer:
                        parts.append(f"    Source: {buyer['source_url']}")
            if "strategic" in buyers:
                parts.append("\nStrategic Acquirers:")
                for buyer in buyers["strategic"]:
                    parts.append(f"\n  - Name: {buyer.get('name', 'N/A')}")
                    parts.append(f"    Strategy: {buyer.get('strategy', 'N/A')}")

    return "\n".join(parts)


def web_search_with_gemini(query: str) -> str:
    """
    Use Gemini with Google Search Grounding to search the web.

    How this works:
    1. We send a query to Gemini with "grounding" enabled
    2. Gemini searches Google, reads the results, and gives us a summary
    3. It includes citations (links) to where it found the info

    Args:
        query: What to search for, e.g. "HVAC M&A EBITDA multiples 2025"

    Returns:
        A string with the search results and any citations
    """
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=query,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            ),
        )

        # Extract the text response
        result_text = response.text if response.text else ""

        # Extract grounding metadata (source URLs)
        citations = []
        if response.candidates and response.candidates[0].grounding_metadata:
            gm = response.candidates[0].grounding_metadata
            if gm.grounding_chunks:
                for chunk in gm.grounding_chunks:
                    if chunk.web:
                        title = chunk.web.title or "Source"
                        uri = chunk.web.uri or ""
                        citations.append(f"- [{title}]({uri})")

        if citations:
            result_text += "\n\n### Sources:\n" + "\n".join(citations)

        return result_text if result_text else "No results found."

    except Exception as e:
        return f"Web search failed: {str(e)}"


def generate_section(prompt: str, context: str, industry: str) -> str:
    """
    Send a prompt to Gemini and get back a section of the report.

    Args:
        prompt: The section-specific prompt template
        context: The data/facts to include
        industry: Industry name for placeholder replacement

    Returns:
        Generated Markdown text for that report section
    """
    from agent.prompts import MASTER_SYSTEM_PROMPT

    # Fill in the placeholders in the prompt
    filled_prompt = prompt.format(industry=industry, context=context)

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=filled_prompt,
            config=types.GenerateContentConfig(
                system_instruction=MASTER_SYSTEM_PROMPT,
            ),
        )

        return response.text if response.text else "*Section generation failed — no response from Gemini.*"

    except Exception as e:
        return f"*Error generating section: {str(e)}*"


def generate_section_with_search(
    prompt: str, search_queries: list[str], kb_context: str, industry: str
) -> str:
    """
    Enhanced version: searches the web first, then generates the section.

    Flow:
    1. Run web searches for fresh data
    2. Combine web results with knowledge base data
    3. Send everything to Gemini to generate the section

    Args:
        prompt: Section prompt template
        search_queries: List of queries to web search
        kb_context: Pre-formatted knowledge base context
        industry: Industry name

    Returns:
        Generated section text
    """
    # Step 1: Run web searches
    web_results = []
    for query in search_queries:
        result = web_search_with_gemini(query)
        web_results.append(f"### Web Search: {query}\n{result}")
        # Small delay to respect rate limits on free tier
        time.sleep(2)

    # Step 2: Combine all context
    combined_context = kb_context
    if web_results:
        combined_context += "\n\n=== WEB SEARCH RESULTS (current data) ===\n"
        combined_context += "\n\n".join(web_results)

    # Step 3: Generate the section
    return generate_section(prompt, combined_context, industry)
