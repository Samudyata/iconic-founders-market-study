# IFG Industry Market Study Agent

AI-powered M&A market study generator for lower middle market blue-collar industries. Built for Iconic Founders Group.

## Live Demo
**[iconic-founders-market-study.streamlit.app](https://iconic-founders-market-study.streamlit.app)**

## What It Does
Select an industry → AI generates a complete IB-quality market study with:
- Executive Industry Snapshot (market size, growth, PE activity)
- EBITDA Multiples by Deal Size (with source citations)
- Color-Coded Valuation Heat Map (what drives 4x vs 8x+ multiples)
- Value Driver Sensitivity Analysis
- Recent Transaction Activity (minimum 5 deals)
- Ideal Buyer Universe (PE platforms + strategics)
- Secondary / Logical Buyers
- Buyer Targeting Strategy
- Deal Thesis Summary
- Risks & Multiple Compression Factors
- **AI Self-Critique** (reviews its own report as a skeptical MD)
- Sources & Methodology with confidence scoring

## Supported Industries
HVAC | Commercial Landscaping | Pest Control | Roofing | Environmental Remediation | Wastewater Services | Industrial Services

## Differentiating Features

| Feature | What It Does |
|---------|--------------|
| **Confidence Scoring** | Every data point tagged HIGH/MEDIUM/LOW with colored badges |
| **Valuation Heat Map** | Color-coded table showing what separates a 4x from an 8x+ company |
| **Self-Critique** | AI critiques its own report from a skeptical MD's perspective |
| **Source Citations** | Every number backed by a `[Source]` tag — no hallucinated data |
| **PDF Export** | IB-style formatted PDF with cover page, tables, branded headers |

## Architecture

```
User selects industry
  → Load curated knowledge base (JSON with source URLs)
  → 12-step sequential prompt chain via Gemini 2.5 Flash
  → Each step: KB data + Google Search Grounding → LLM generation
  → Self-critique pass (feeds full report back for MD-level review)
  → Render in Streamlit tabs + downloadable PDF
```

**Stack:** Python, Streamlit, Google Gemini 2.5 Flash (free tier), fpdf2

**Key Design Decisions:**
- **Curated JSON knowledge base** as reliability floor — every data point has a `source_url`
- **Google Search Grounding** for real-time web data with automatic citations
- **Anti-hallucination guardrails** — constrained prompts require sources, allow "Limited data available"
- **Confidence scoring** — HIGH (published source), MEDIUM (web search), LOW (directional only)
- **IB tone enforcement** — master system prompt sets VP-level writing standard across all sections

## Setup

```bash
# Clone
git clone https://github.com/Samudyata/iconic-founders-market-study.git
cd iconic-founders-market-study

# Install dependencies
pip install -r requirements.txt

# Add your Gemini API key
echo "GOOGLE_API_KEY=your_key_here" > .env

# Run
streamlit run app.py
```

Get a free Gemini API key at https://aistudio.google.com/apikey

## Data Sources
- First Page Sage (EBITDA multiples by industry)
- Capstone Partners (M&A market reports)
- PKF O'Connor Davies (transaction data)
- S&P Global / PitchBook (deal flow data)
- BizBuySell (small business valuation benchmarks)
- NYU Stern / Damodaran (public company multiples)
- Google Search via Gemini (real-time data)

See [`docs/data_sources.md`](docs/data_sources.md) for detailed sourcing methodology.

## Sample Output
See [`sample_output/`](sample_output/) for a complete HVAC market study (Markdown + PDF).

## What I'd Build Next
See [`docs/improvements.md`](docs/improvements.md) for the full list. Top priorities:
1. **Pydantic structured output** — typed models that reject outputs without citations
2. **Multi-industry comparison** — side-by-side multiples and buyer activity
3. **Company-specific valuation estimator** — personalized "Where You Sit on the Heat Map"
4. **Automated data refresh** — scrapers that update the knowledge base weekly
5. **Chat follow-up interface** — ask questions about the generated report

## Author
Samudyata Jagirdar — MS Computer Engineering, Arizona State University
