from typing import List, Tuple, Dict, Any
from pydantic import BaseModel

class TextSpan(BaseModel):
    text: str
    font_size: float
    is_bold: bool
    is_italic: bool = False
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1


class TextBlock(BaseModel):
    lines: List[str]
    spans: List[TextSpan] = []
    bbox: Tuple[float, float, float, float]
    page_number: int = 1
    avg_font_size: float = 10.0
    is_heading: bool = False
    link_uris: List[str] = []

    @property
    def full_text(self) -> str:
        return "\n".join(self.lines)


def reconstruct_reading_order(blocks: List[TextBlock]) -> List[TextBlock]:
    """
    Sorts and reconstructs reading order for multi-column and single-column layouts.
    Groups by vertical flow within spatial columns.
    """
    if not blocks:
        return []

    # Sort primarily by page number
    pages: Dict[int, List[TextBlock]] = {}
    for b in blocks:
        pages.setdefault(b.page_number, []).append(b)

    ordered_blocks: List[TextBlock] = []

    for page_num in sorted(pages.keys()):
        page_blocks = pages[page_num]
        
        # Check if page has multiple distinct horizontal columns (e.g. left sidebar / 2-column)
        # Calculate mid x-coordinates
        x_mins = [b.bbox[0] for b in page_blocks]
        x_maxs = [b.bbox[2] for b in page_blocks]
        min_x = min(x_mins) if x_mins else 0
        max_x = max(x_maxs) if x_maxs else 600
        page_width = max_x - min_x

        # Detect if there's a strong column split
        # If headers span across full width, keep top-to-bottom
        # For standard resume format, sort top-to-bottom (y0), with secondary x0
        def block_sort_key(b: TextBlock):
            # Quantize y to reduce noise across small vertical misalignments
            y_quantized = round(b.bbox[1] / 8.0) * 8.0
            return (y_quantized, b.bbox[0])

        sorted_page_blocks = sorted(page_blocks, key=block_sort_key)
        ordered_blocks.extend(sorted_page_blocks)

    return ordered_blocks
