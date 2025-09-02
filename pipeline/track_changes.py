from lxml import etree
from docx.text.paragraph import Paragraph

def apply_diffs_to_paragraph(par: Paragraph, diffs, author="LLM", date_iso="2025-08-28T00:00:00Z"):
    p = par._element
    # wipe runs; rebuild from diffs with w:r + w:t, wrapping ins/del
    # create <w:ins w:author="..." w:date="..."> ... </w:ins> and <w:del ...>
    # keep run properties minimal (rPr) to avoid style bloat
    # NOTE: implement carefully; test with short paragraphs first
