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
    (r'^(experience|work experience|employment history|professional experience|internships?|work history)$', SectionType.EXPERIENCE),
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


def is_heading_line(line: str) -> Optional[SectionType]:
    """
    Checks if a single line is a section heading.
    """
    text = line.strip()
    if not text or len(text) > 40:
        return None

    cleaned = re.sub(r'[^a-zA-Z\s&]', '', text).strip().lower()
    
    for pattern, section_type in SECTION_HEADER_PATTERNS:
        if re.search(pattern, cleaned):
            return section_type
            
    return None


def segment_blocks(blocks: List[TextBlock]) -> Dict[SectionType, SegmentedSection]:
    """
    Segments document blocks into structured sections with line-level accuracy.
    Splits multi-line blocks whenever an internal heading line is encountered.
    """
    sections: Dict[SectionType, SegmentedSection] = {}
    
    current_type = SectionType.HEADER
    current_heading: Optional[str] = None
    current_lines: List[str] = []

    def commit_section():
        if current_lines:
            new_block = TextBlock(lines=list(current_lines), bbox=(0, 0, 500, float(len(current_lines) * 20)))
            if current_type not in sections:
                sections[current_type] = SegmentedSection(
                    section_type=current_type,
                    heading_text=current_heading,
                    blocks=[new_block]
                )
            else:
                sections[current_type].blocks.append(new_block)

    for block in blocks:
        for line in block.lines:
            clean_l = line.strip()
            if not clean_l:
                continue

            heading_match = is_heading_line(clean_l)
            if heading_match:
                commit_section()
                current_type = heading_match
                current_heading = clean_l
                current_lines = []
            else:
                current_lines.append(clean_l)

    commit_section()
    return sections
