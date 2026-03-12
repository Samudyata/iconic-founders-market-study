"""
PDF Generator
=============
Converts a MarketStudy object into a professional IB-style PDF.

Uses fpdf2 — a pure-Python library with zero system dependencies.
This means it works on Streamlit Cloud without any extra setup.

Teaching note: PDF generation is basically "drawing" text, lines, and boxes
onto a page. We control everything: fonts, positions, colors, margins.
fpdf2 gives us low-level control which is perfect for IB-style formatting.
"""

import re
from fpdf import FPDF


# --- IFG Brand Colors (RGB) ---
NAVY = (14, 17, 23)        # Background / header bars
GOLD = (201, 168, 76)      # Accent / titles
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)
TEXT_COLOR = (50, 50, 50)


class IFGReport(FPDF):
    """
    Custom PDF class with IFG branding.

    Teaching note: By subclassing FPDF, we can override header() and footer()
    so they automatically appear on every page.
    """

    def __init__(self, industry: str, date: str):
        super().__init__()
        self.industry = industry
        self.report_date = date
        # Use built-in fonts only (no TTF needed)
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        """Runs automatically at the top of every page."""
        # Gold line at the top
        self.set_draw_color(*GOLD)
        self.set_line_width(0.8)
        self.line(10, 10, self.w - 10, 10)

        # Company name
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*DARK_GRAY)
        self.set_y(12)
        self.cell(0, 5, "Iconic Founders Group  |  Lower Middle Market M&A Advisory", align="L")

        # Date on the right
        self.set_font("Helvetica", "", 8)
        self.set_y(12)
        self.cell(0, 5, self.report_date, align="R")

        self.ln(10)

    def footer(self):
        """Runs automatically at the bottom of every page."""
        self.set_y(-20)
        # Gold line
        self.set_draw_color(*GOLD)
        self.set_line_width(0.5)
        self.line(10, self.h - 20, self.w - 10, self.h - 20)

        # Page number
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*DARK_GRAY)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def add_cover_page(self):
        """Create a professional cover page."""
        self.add_page()

        # Big vertical space
        self.ln(50)

        # Gold decorative line
        self.set_draw_color(*GOLD)
        self.set_line_width(1.5)
        self.line(30, self.get_y(), self.w - 30, self.get_y())
        self.ln(15)

        # Main title
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(*TEXT_COLOR)
        self.cell(0, 15, "Industry Market Study", align="C")
        self.ln(18)

        # Industry name
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(*GOLD)
        self.cell(0, 12, self.industry, align="C")
        self.ln(20)

        # Another gold line
        self.set_draw_color(*GOLD)
        self.line(30, self.get_y(), self.w - 30, self.get_y())
        self.ln(15)

        # Subtitle
        self.set_font("Helvetica", "", 12)
        self.set_text_color(*DARK_GRAY)
        self.cell(0, 8, "Lower Middle Market M&A Advisory", align="C")
        self.ln(8)
        self.cell(0, 8, "Pre-Engagement Research Report", align="C")
        self.ln(20)

        # Date
        self.set_font("Helvetica", "I", 11)
        self.cell(0, 8, f"Prepared: {self.report_date}", align="C")
        self.ln(30)

        # Disclaimer
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*LIGHT_GRAY)
        self.multi_cell(0, 4,
            "CONFIDENTIAL - This report is based on publicly available data and "
            "AI-assisted research. It is intended for pre-engagement discussion "
            "purposes and should not be relied upon as a formal valuation.",
            align="C"
        )

    def add_section(self, title: str, content: str):
        """
        Add a report section with proper formatting.

        Parses basic Markdown (headers, bold, bullets, tables) into PDF elements.
        """
        self.add_page()

        # Section title with gold underline
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*TEXT_COLOR)
        self.cell(0, 10, title)
        self.ln(2)
        self.set_draw_color(*GOLD)
        self.set_line_width(0.8)
        self.line(10, self.get_y() + 8, self.w - 10, self.get_y() + 8)
        self.ln(12)

        # Parse and render content
        self._render_markdown(content)

    def _render_markdown(self, text: str):
        """
        Simple Markdown-to-PDF renderer.

        Handles: headers (##, ###), bold (**text**), bullets (- ), tables (| |),
        horizontal rules (---), and regular paragraphs.
        """
        if not text:
            return

        lines = text.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines
            if not line:
                self.ln(3)
                i += 1
                continue

            # Horizontal rule
            if line.startswith("---"):
                self.set_draw_color(*LIGHT_GRAY)
                self.set_line_width(0.3)
                self.line(10, self.get_y() + 2, self.w - 10, self.get_y() + 2)
                self.ln(6)
                i += 1
                continue

            # H2 header
            if line.startswith("## "):
                self.ln(4)
                self.set_font("Helvetica", "B", 14)
                self.set_text_color(*TEXT_COLOR)
                header_text = line[3:].strip()
                header_text = self._strip_markdown(header_text)
                self.cell(0, 8, header_text)
                self.ln(10)
                i += 1
                continue

            # H3 header
            if line.startswith("### "):
                self.ln(3)
                self.set_font("Helvetica", "B", 11)
                self.set_text_color(*GOLD)
                header_text = line[4:].strip()
                header_text = self._strip_markdown(header_text)
                self.cell(0, 7, header_text)
                self.ln(8)
                i += 1
                continue

            # Table detection (lines starting with |)
            if line.startswith("|"):
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    table_lines.append(lines[i].strip())
                    i += 1
                self._render_table(table_lines)
                self.ln(4)
                continue

            # Bullet point
            if line.startswith("- ") or line.startswith("* "):
                self.set_font("Helvetica", "", 10)
                self.set_text_color(*TEXT_COLOR)
                bullet_text = line[2:].strip()
                bullet_text = self._strip_markdown(bullet_text)
                # Indent + bullet character
                self.set_x(15)
                self.cell(5, 5, "-")
                self.multi_cell(self.w - 30, 5, bullet_text)
                self.ln(1)
                i += 1
                continue

            # Numbered list (1. 2. 3.)
            if re.match(r"^\d+\.\s", line):
                self.set_font("Helvetica", "", 10)
                self.set_text_color(*TEXT_COLOR)
                num_match = re.match(r"^(\d+\.)\s(.+)", line)
                if num_match:
                    num = num_match.group(1)
                    item_text = self._strip_markdown(num_match.group(2))
                    self.set_x(15)
                    self.cell(8, 5, num)
                    self.multi_cell(self.w - 33, 5, item_text)
                    self.ln(1)
                i += 1
                continue

            # Regular paragraph
            self.set_font("Helvetica", "", 10)
            self.set_text_color(*TEXT_COLOR)
            clean_line = self._strip_markdown(line)
            if clean_line:
                self.multi_cell(0, 5, clean_line)
                self.ln(2)
            i += 1

    def _strip_markdown(self, text: str) -> str:
        """Remove Markdown formatting characters for plain text rendering."""
        # Remove bold markers
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        # Remove italic markers
        text = re.sub(r"\*(.+?)\*", r"\1", text)
        # Remove inline code
        text = re.sub(r"`(.+?)`", r"\1", text)
        # Remove links — keep text, drop URL
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        # Remove emoji (common ones that break Latin-1)
        text = re.sub(r"[\U0001F300-\U0001F9FF]", "", text)
        text = re.sub(r"[\u2600-\u27BF]", "", text)
        # Replace special characters that aren't in Latin-1
        text = text.replace("\u2019", "'")  # right single quote
        text = text.replace("\u2018", "'")  # left single quote
        text = text.replace("\u201c", '"')  # left double quote
        text = text.replace("\u201d", '"')  # right double quote
        text = text.replace("\u2013", "-")  # en dash
        text = text.replace("\u2014", "--") # em dash
        text = text.replace("\u2026", "...") # ellipsis
        text = text.replace("\u00b7", "-")  # middle dot
        text = text.replace("\u2022", "-")  # bullet
        text = text.replace("\u25cf", "-")  # black circle
        # Strip any remaining non-Latin-1 characters
        text = text.encode("latin-1", errors="replace").decode("latin-1")
        # Confidence badges — convert to plain text
        text = text.replace("[HIGH CONFIDENCE]", "(HIGH)")
        text = text.replace("[MEDIUM CONFIDENCE]", "(MEDIUM)")
        text = text.replace("[LOW CONFIDENCE]", "(LOW)")
        return text.strip()

    def _render_table(self, table_lines: list[str]):
        """Render a Markdown table as a PDF table."""
        if not table_lines:
            return

        # Parse header row
        rows = []
        for line in table_lines:
            # Skip separator rows (|---|---|)
            if re.match(r"^\|[\s\-:]+\|", line):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            cells = [self._strip_markdown(c) for c in cells]
            rows.append(cells)

        if not rows:
            return

        # Calculate column widths based on content
        num_cols = max(len(r) for r in rows)
        usable_width = self.w - 20  # margins
        col_width = usable_width / num_cols

        # Header row (first row)
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(40, 50, 65)  # Dark blue-gray
        self.set_text_color(*WHITE)

        if rows:
            for j, cell in enumerate(rows[0]):
                w = col_width
                self.cell(w, 7, cell[:30], border=1, fill=True, align="C")
            self.ln()

        # Data rows
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*TEXT_COLOR)

        for row_idx, row in enumerate(rows[1:]):
            # Alternate row shading
            if row_idx % 2 == 0:
                self.set_fill_color(240, 240, 240)
            else:
                self.set_fill_color(*WHITE)

            for j, cell in enumerate(row):
                w = col_width
                self.cell(w, 6, cell[:30], border=1, fill=True, align="L")
            self.ln()


def generate_pdf(study) -> bytes:
    """
    Convert a MarketStudy object into a PDF and return it as bytes.

    This is the main function — called from app.py to create the downloadable PDF.

    Args:
        study: A MarketStudy dataclass instance with all sections filled in

    Returns:
        PDF file as bytes (ready for st.download_button)
    """
    pdf = IFGReport(industry=study.industry, date=study.generated_at)
    pdf.alias_nb_pages()  # Enable {nb} total page count in footer

    # Cover page
    pdf.add_cover_page()

    # Each section gets its own page
    sections = [
        ("Executive Industry Snapshot", study.executive_snapshot),
        ("EBITDA Multiples by Deal Size", study.ebitda_multiples),
        ("Valuation Heat Map", study.valuation_heatmap),
        ("Value Driver Sensitivity", study.value_drivers),
        ("Recent Transaction Activity", study.recent_transactions),
        ("Ideal Buyer Universe", study.ideal_buyers),
        ("Secondary / Logical Buyers", study.secondary_buyers),
        ("Buyer Targeting Strategy", study.buyer_targeting),
        ("Deal Thesis Summary", study.deal_thesis),
        ("Risks & Multiple Compression Factors", study.risks),
        ("Self-Critique", study.self_critique),
        ("Sources & Methodology", study.sources),
    ]

    for title, content in sections:
        if content:
            pdf.add_section(title, content)

    # Return as bytes (fpdf2 returns bytearray, Streamlit needs bytes)
    return bytes(pdf.output())
