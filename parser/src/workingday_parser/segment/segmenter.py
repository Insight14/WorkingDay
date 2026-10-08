import re
from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel
from ..ingest.layout import TextBlock

class SectionType(str, Enum):
    HEADER = "header"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    SKILLS = "skills"
    PROJECTS = "projects"
    SUMMARY = "summary"
    CERTIFICATIONS = "certifications"
    OTHER = "other"


SECTION_HEADER_PATTERNS = [
    (r'^(education|academic background|academic history)$', SectionType.EDUCATION),
    (r'^(experience|work experience|employment history|professional experience|internships?)$', SectionType.EXPERIENCE),
    (r'^(technical skills|skills|technologies|core competencies|skills & abilities)$', SectionType.SKILLS),
    (r'^(projects|personal projects|key projects|academic projects)$', SectionType.PROJECTS),
    (r'^(summary|professional summary|about me|profile)$', SectionType.SUMMARY),
    (r'^(certifications?|licenses?|credentials?)$', SectionType.CERTIFICATIONS),
]


class SegmentedSection(BaseModel):
    section_type: SectionType
    heading_text: Optional[str] = None
    blocks: List[TextBlock] = []

    @property
    def raw_text(self) -> str:
        return "\n".join(b.full_text for b in self.blocks)


def is_heading_block(block: TextBlock, max_page_font: float = 12.0) -> Optional[SectionType]:
    text = block.full_text.strip()
    if not text or len(text) > 50:  # Section headings are short
        return None

    cleaned = re.sub(r'[^a-zA-Z\s&]', '', text).strip().lower()
    
    for pattern, section_type in SECTION_HEADER_PATTERNS:
        if re.search(pattern, cleaned):
            return section_type
            
    return None


def segment_blocks(blocks: List[TextBlock]) -> Dict[SectionType, SegmentedSection]:
    """
    Segments document blocks into structured sections.
    The first block(s) prior to the first major heading are classified as HEADER.
    """
    sections: Dict[SectionType, SegmentedSection] = {}
    
    current_type = SectionType.HEADER
    current_heading: Optional[str] = None
    current_blocks: List[TextBlock] = []

    for block in blocks:
        heading_type = is_heading_block(block)
        if heading_type:
            # Save previous section
            if current_blocks:
                if current_type not in sections:
                    sections[current_type] = SegmentedSection(
                        section_type=current_type,
                        heading_text=current_heading,
                        blocks=current_blocks
                    )
                else:
                    sections[current_type].blocks.extend(current_blocks)
            
            # Start new section
            current_type = heading_type
            current_heading = block.full_text.strip()
            current_blocks = []
        else:
            current_blocks.append(block)

    # Save remaining blocks
    if current_blocks:
        if current_type not in sections:
            sections[current_type] = SegmentedSection(
                section_type=current_type,
                heading_text=current_heading,
                blocks=current_blocks
            )
        else:
            sections[current_type].blocks.extend(current_blocks)

    return sections
