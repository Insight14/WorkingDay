import io
import os
from typing import List, Tuple, Optional
import fitz  # PyMuPDF
import pdfplumber
from docx import Document

from .layout import TextBlock, TextSpan, reconstruct_reading_order

def extract_pdf_with_pymupdf(file_bytes: bytes) -> Tuple[List[TextBlock], List[str]]:
    """
    Extracts text blocks with precise font sizes, bold flags, bboxes,
    and PDF link annotations (hyperlink URIs) from PyMuPDF.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    blocks: List[TextBlock] = []
    all_links: List[str] = []

    for page_idx, page in enumerate(doc):
        page_links = page.get_links()
        for link in page_links:
            if "uri" in link and link["uri"]:
                all_links.append(link["uri"])

        # Extract structured text with flags (font size, bold, etc.)
        text_page = page.get_text("dict", flags=fitz.TEXTFLAGS_SEARCH)
        
        for b in text_page.get("blocks", []):
            if b.get("type") == 0:  # Text block
                block_lines: List[str] = []
                block_spans: List[TextSpan] = []
                font_sizes: List[float] = []

                for l in b.get("lines", []):
                    line_text = ""
                    for s in l.get("spans", []):
                        stext = s.get("text", "")
                        line_text += stext
                        fsize = float(s.get("size", 10.0))
                        font_sizes.append(fsize)
                        flags = s.get("flags", 0)
                        # PyMuPDF font flag 2 is bold, 1 is superscript, 4 is italic
                        is_bold = bool(flags & 2) or ("bold" in s.get("font", "").lower())
                        is_italic = bool(flags & 4) or ("italic" in s.get("font", "").lower())
                        
                        bbox = tuple(s.get("bbox", (0, 0, 0, 0)))
                        block_spans.append(TextSpan(
                            text=stext,
                            font_size=fsize,
                            is_bold=is_bold,
                            is_italic=is_italic,
                            bbox=bbox
                        ))
                    if line_text.strip():
                        block_lines.append(line_text)

                if block_lines:
                    bbox = tuple(b.get("bbox", (0, 0, 0, 0)))
                    avg_size = sum(font_sizes) / len(font_sizes) if font_sizes else 10.0
                    
                    # Check if any link annotation rect intersects with this block's bbox
                    matched_uris = []
                    for link in page_links:
                        if "uri" in link and "from" in link:
                            link_rect = link["from"]
                            # Check overlap with bbox
                            if not (link_rect.x1 < bbox[0] or link_rect.x0 > bbox[2] or
                                    link_rect.y1 < bbox[1] or link_rect.y0 > bbox[3]):
                                matched_uris.append(link["uri"])

                    blocks.append(TextBlock(
                        lines=block_lines,
                        spans=block_spans,
                        bbox=bbox,
                        page_number=page_idx + 1,
                        avg_font_size=avg_size,
                        link_uris=matched_uris
                    ))

    doc.close()
    return reconstruct_reading_order(blocks), all_links


def extract_pdf_with_pdfplumber_fallback(file_bytes: bytes) -> List[TextBlock]:
    """Fallback extraction using pdfplumber."""
    blocks: List[TextBlock] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                lines = [l for l in text.split("\n") if l.strip()]
                blocks.append(TextBlock(
                    lines=lines,
                    bbox=(0, 0, float(page.width), float(page.height)),
                    page_number=page_idx + 1,
                    avg_font_size=10.0
                ))
    return blocks


def extract_docx(file_bytes: bytes) -> List[TextBlock]:
    """Extracts text blocks and headings from a DOCX file."""
    doc = Document(io.BytesIO(file_bytes))
    blocks: List[TextBlock] = []
    for p_idx, p in enumerate(doc.paragraphs):
        text = p.text.strip()
        if text:
            is_heading = p.style.name.startswith("Heading") if p.style else False
            blocks.append(TextBlock(
                lines=[text],
                bbox=(0, float(p_idx * 20), 500, float(p_idx * 20 + 20)),
                page_number=1,
                is_heading=is_heading
            ))
    return blocks


def ingest_document(file_bytes: bytes, filename: str) -> Tuple[List[TextBlock], List[str]]:
    """
    Main ingestion entrypoint. Supports PDF and DOCX, with automatic fallbacks.
    """
    ext = os.path.splitext(filename.lower())[1]
    if ext == ".docx":
        return extract_docx(file_bytes), []
    
    # Try PyMuPDF
    try:
        blocks, links = extract_pdf_with_pymupdf(file_bytes)
        if blocks and any(b.lines for b in blocks):
            return blocks, links
    except Exception:
        pass

    # Fallback to pdfplumber
    try:
        blocks = extract_pdf_with_pdfplumber_fallback(file_bytes)
        if blocks:
            return blocks, []
    except Exception:
        pass

    return [], []
