import re
from typing import List, Dict, Optional, Any
from ..models import (
    ResumeData, NameModel, AddressModel, LinksModel,
    EducationItem, ExperienceItem, ProjectItem, FieldWithMeta
)
from ..ingest.layout import TextBlock
from ..ingest.bullets import rebuild_bullet_list, is_bullet_start
from ..segment.segmenter import segment_blocks, SectionType
from ..rules.name import parse_name
from ..rules.address import parse_address_block
from ..rules.links import extract_links_from_text_and_uris, extract_contact_info
from ..rules.education import parse_education_block
from ..rules.experience import build_experience_item, DATE_RANGE_REGEX
from ..llm.interface import LLMExtractorInterface, MockLLMExtractor

def extract_skills_dict(skills_text: str) -> Dict[str, List[str]]:
    skills: Dict[str, List[str]] = {}
    lines = [l.strip() for l in skills_text.split("\n") if l.strip()]
    for line in lines:
        if "|" in line:
            cat, items_str = line.split("|", 1)
            cat = cat.strip()
            items = [re.sub(r'^[•\s]+|[.\s]+$', '', item.strip()) for item in items_str.split(",") if item.strip()]
            if items:
                skills[cat] = items
        else:
            items = [re.sub(r'^[•\s]+|[.\s]+$', '', item.strip()) for item in line.split(",") if item.strip()]
            if items:
                skills.setdefault("General", []).extend(items)
    return skills


def extract_projects_list(blocks: List[TextBlock]) -> List[ProjectItem]:
    projects: List[ProjectItem] = []
    lines: List[str] = []
    for b in blocks:
        lines.extend(b.lines)

    current_name = ""
    current_category = ""
    current_raw_bullets: List[str] = []

    def commit_project():
        if current_name:
            bullets = rebuild_bullet_list(current_raw_bullets)
            projects.append(ProjectItem(
                name=FieldWithMeta(value=current_name, confidence=0.95),
                category=FieldWithMeta(value=current_category if current_category else None, confidence=0.9),
                bullets=FieldWithMeta(value=bullets, confidence=0.95),
                technologies=FieldWithMeta(value=[]),
                link=FieldWithMeta(value=None, flag="empty_in_resume")
            ))

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.lower().startswith("project |") or (re.search(r'\b(personal project|group project|academic project)\b', stripped, re.IGNORECASE) and not is_bullet_start(stripped)):
            commit_project()
            current_raw_bullets = []
            
            clean_proj = re.sub(r'^Project\s*\|\s*', '', stripped, flags=re.IGNORECASE).strip()
            cat_match = re.search(r'\b(Personal Project|Group Project|Academic Project|Open Source)\b', clean_proj, re.IGNORECASE)
            if cat_match:
                current_category = cat_match.group(0).strip()
                current_name = clean_proj[:cat_match.start()].strip(" -|")
            else:
                current_category = "Project"
                current_name = clean_proj
        elif is_bullet_start(stripped) or current_name:
            current_raw_bullets.append(stripped)

    commit_project()
    return projects


def extract_experience_list(blocks: List[TextBlock]) -> List[ExperienceItem]:
    """
    Extracts experience items and groups bullets under job headers.
    Supports both single-line ('Title - Company Date') and multi-line ('Title - Company\nDate') headers.
    """
    items: List[ExperienceItem] = []
    all_lines: List[str] = []
    for b in blocks:
        all_lines.extend(b.lines)

    current_header: Optional[str] = None
    current_bullet_lines: List[str] = []

    def commit_exp():
        if current_header and current_header.strip():
            bullets = rebuild_bullet_list(current_bullet_lines)
            exp_item = build_experience_item(current_header, bullets)
            if exp_item.company.value or exp_item.title.value:
                items.append(exp_item)

    i = 0
    while i < len(all_lines):
        line = all_lines[i].strip()
        if not line:
            i += 1
            continue

        # Check if line is a date or contains date range
        has_date = bool(DATE_RANGE_REGEX.search(line) or ("present" in line.lower() and ("-" in line or "–" in line or "to" in line.lower())))
        is_bullet = is_bullet_start(line)

        if not is_bullet:
            if has_date:
                # If current_header already exists and has NO date, merge this date line into it!
                if current_header and not DATE_RANGE_REGEX.search(current_header) and "present" not in current_header.lower():
                    current_header = f"{current_header} {line}"
                else:
                    commit_exp()
                    current_header = line
                    current_bullet_lines = []
            elif " - " in line or " – " in line or " | " in line or re.search(r'\b(intern|engineer|developer|assistant|officer|mentor|instructor|specialist|manager|lead|director|analyst|associate)\b', line, re.IGNORECASE):
                # Likely a title/company line
                commit_exp()
                current_header = line
                current_bullet_lines = []
            else:
                if current_header:
                    current_bullet_lines.append(line)
                else:
                    current_header = line
        else:
            if current_header:
                current_bullet_lines.append(line)

        i += 1

    commit_exp()
    return items


def extract_education_list(blocks: List[TextBlock]) -> List[EducationItem]:
    items: List[EducationItem] = []
    all_lines: List[str] = []
    for b in blocks:
        all_lines.extend(b.lines)

    i = 0
    while i < len(all_lines):
        line = all_lines[i].strip()
        if not line:
            i += 1
            continue

        next_line = all_lines[i+1].strip() if i + 1 < len(all_lines) else None
        edu = parse_education_block(line, next_line)
        items.append(edu)
        
        if next_line and (re.search(r'\b(bachelor|master|phd|bs|ms|degree|in\s+computer)\b', next_line, re.IGNORECASE)):
            i += 2
        else:
            i += 1

    return items


class WorkingDayExtractor:
    def __init__(self, llm_extractor: Optional[LLMExtractorInterface] = None):
        self.llm = llm_extractor or MockLLMExtractor()

    def extract_from_blocks(
        self,
        blocks: List[TextBlock],
        annotation_links: Optional[List[str]] = None,
        put_additional_given_in_middle: bool = False
    ) -> ResumeData:
        sections = segment_blocks(blocks)
        
        # 1. Process Header Section
        header_sec = sections.get(SectionType.HEADER)
        header_text = header_sec.raw_text if header_sec else ""
        header_lines = [l.strip() for l in header_text.split("\n") if l.strip()]

        full_resume_text = "\n".join(b.full_text for b in blocks)

        email, phone = extract_contact_info(header_text or full_resume_text)
        links = extract_links_from_text_and_uris(header_text or full_resume_text, annotation_links)

        raw_name = ""
        for line in header_lines:
            if "@" in line or (re.search(r'\d{3}', line) and "|" in line):
                continue
            if re.search(r'^[A-Za-z\s.,\'-]+$', line) and len(line.split()) >= 2:
                raw_name = line
                break
                
        if not raw_name and header_lines:
            raw_name = header_lines[0]

        name_model = parse_name(
            raw_name=raw_name,
            email=email,
            linkedin_url=links.linkedin.value,
            put_additional_given_in_middle=put_additional_given_in_middle
        )

        address_model = parse_address_block(header_text)

        # 2. Process Education Section
        edu_sec = sections.get(SectionType.EDUCATION)
        education_items = extract_education_list(edu_sec.blocks) if edu_sec else []

        # 3. Process Experience Section
        exp_sec = sections.get(SectionType.EXPERIENCE)
        experience_items = extract_experience_list(exp_sec.blocks) if exp_sec else []

        # 4. Process Projects Section
        proj_sec = sections.get(SectionType.PROJECTS)
        project_items = extract_projects_list(proj_sec.blocks) if proj_sec else []

        # 5. Process Skills Section
        skills_sec = sections.get(SectionType.SKILLS)
        skills_dict = extract_skills_dict(skills_sec.raw_text) if skills_sec else {}

        return ResumeData(
            name=name_model,
            email=FieldWithMeta(value=email, confidence=0.98 if email else 1.0, flag=None if email else "empty_in_resume"),
            phone=FieldWithMeta(value=phone, confidence=0.98 if phone else 1.0, flag=None if phone else "empty_in_resume"),
            address=address_model,
            links=links,
            education=education_items,
            experience=experience_items,
            projects=project_items,
            skills=skills_dict,
            raw_text=full_resume_text
        )
