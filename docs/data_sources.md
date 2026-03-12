# Data Sources

This document lists every data source used by the IFG Market Study Agent, how it's accessed, and what data it provides.

## Curated Knowledge Base (JSON Files)

These are pre-researched JSON files with cited data points. They serve as the **reliability floor** — even if web search fails, reports contain real, sourced data.

### Industry Data (`data/industries/*.json`)

| Industry | File | Key Data |
|----------|------|----------|
| HVAC | `hvac.json` | EBITDA multiples by deal size, value drivers, 5+ recent transactions, known PE/strategic buyers |
| Commercial Landscaping | `landscaping.json` | Same schema |
| Pest Control | `pest_control.json` | Same schema |
| Roofing | `roofing.json` | Same schema |
| Environmental Remediation | `remediation.json` | Same schema |
| Wastewater Services | `wastewater.json` | Same schema |
| Industrial Services | `industrial_services.json` | Same schema |

### Buyer Data (`data/buyers/*.json`)

| File | Contents |
|------|----------|
| `pe_firms.json` | Cross-industry PE firms active in blue-collar/trades M&A |
| `strategic_buyers.json` | Large strategic acquirers with roll-up strategies |

### Data Schema (per industry JSON)

Each industry file follows this structure:

```json
{
  "overview": {
    "market_size": "$XX billion",
    "growth_rate": "X.X% CAGR",
    "fragmentation": "High/Medium/Low",
    "ebitda_margins": "XX-XX%"
  },
  "ebitda_multiples": {
    "$2M-$5M EBITDA": {
      "range": "X.Xx - X.Xx",
      "median": "X.Xx",
      "source": "Source Name",
      "source_url": "https://..."
    }
  },
  "value_drivers": [
    {
      "factor": "Factor Name",
      "impact": "+X.Xx turns",
      "explanation": "Why this matters",
      "source": "Source Name"
    }
  ],
  "recent_transactions": [
    {
      "date": "Q1 2025",
      "target": "Company Name",
      "acquirer": "Buyer Name",
      "type": "Platform/Add-on",
      "deal_size": "$XXM or Undisclosed",
      "source": "Source Name",
      "source_url": "https://..."
    }
  ],
  "known_buyers": {
    "pe_platforms": [...],
    "strategic": [...]
  }
}
```

## Real-Time Web Search (Gemini + Google Search Grounding)

The agent uses **Google Gemini 2.5 Flash** with **Google Search Grounding** enabled. This means:

1. A search query is sent to Gemini (e.g., "HVAC M&A EBITDA multiples 2025")
2. Gemini automatically searches Google, reads results, and synthesizes a response
3. Grounding metadata provides source URLs and titles as citations
4. These citations are appended to each web search result

### Search Queries by Section

| Section | Example Queries |
|---------|----------------|
| Executive Snapshot | `"{industry} industry market size growth 2025"`, `"{industry} private equity M&A activity 2024 2025"` |
| EBITDA Multiples | `"{industry} EBITDA multiples lower middle market 2025"` |
| Recent Transactions | `"{industry} company acquisition deal 2024 2025"`, `"{industry} M&A transaction private equity 2024"` |
| Ideal Buyers | `"private equity firms investing in {industry} companies 2024 2025"` |
| Risks | `"{industry} industry risks challenges 2025 tariffs labor"` |

### Grounding Citation Format

Citations are extracted from `response.candidates[0].grounding_metadata.grounding_chunks` and formatted as:
```
- [Source Title](https://source-url.com)
```

## Source Quality Tiers

Every data point in the report is tagged with a confidence level:

| Tier | Label | Criteria | Visual |
|------|-------|----------|--------|
| 1 | HIGH CONFIDENCE | Directly from a published report with verifiable URL | Green badge |
| 2 | MEDIUM CONFIDENCE | Derived from proxy data, web search, or industry estimates | Orange badge |
| 3 | LOW CONFIDENCE | Directional commentary only; public data insufficient | Red badge |

## Key External Sources Referenced

- **First Page Sage** — EBITDA multiples by industry and company size
- **NYU Stern / Damodaran** — Public company EV/EBITDA benchmarks
- **PitchBook / GF Data** — M&A transaction data and multiples (via web search summaries)
- **IBISWorld** — Industry market size and growth estimates
- **Trade publications** — Industry-specific deal announcements (via web search)
- **SEC / SBIC filings** — PE firm investment activity (via web search)
