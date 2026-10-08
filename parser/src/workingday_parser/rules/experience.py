import re
from typing import Optional, List, Tuple
from ..models import ExperienceItem, FieldWithMeta

MONTH_MAP = {
    "jan": "01", "january": "01",
    "feb": "02", "february": "02",
    "mar": "03", "march": "03",
    "apr": "04", "april": "04",
    "may": "05",
    "jun": "06", "june": "06",
    "jul": "07", "july": "07",
    "aug": "08", "august": "08",
    "sep": "09", "sept": "09", "september": "09",
    "oct": "10", "october": "10",
    "nov": "11", "november": "11",
    "dec": "12", "december": "12"
}

DATE_RANGE_REGEX = re.compile(
    r'(?P<start>(?:[A-Za-z]+|\d{1,2})[\s/.-]+(?:\d{4}|\d{2}))\s*(?:-|–|—|to)\s*(?P<end>Present|Current|(?:[A-Za-z]+|\d{1,2})[\s/.-]+(?:\d{4}|\d{2}))',
    re.IGNORECASE
)

LOCATION_BRACKET_REGEX = re.compile(r'\[(.*?)\]|\((.*?)\)')

def normalize_date(date_str: str) -> Optional[str]:
    if not date_str:
        return None
    cleaned = date_str.strip()
    if cleaned.lower() in ("present", "current"):
        return None
    
    # Check "Month YYYY" or "Mon YYYY"
    m = re.search(r'([A-Za-z]+)\s*(\d{4})', cleaned)
    if m:
        mon_str = m.group(1).lower()
        year_str = m.group(2)
        if mon_str in MONTH_MAP:
            return f"{year_str}-{MONTH_MAP[mon_str]}"
        
    # Check "MM/YYYY" or "M/YYYY"
    m2 = re.search(r'(\d{1,2})[/-](\d{4})', cleaned)
    if m2:
        mon = int(m2.group(1))
        yr = m2.group(2)
        return f"{yr}-{mon:02d}"
        
    # Check year only "YYYY"
    m3 = re.search(r'\b(19\d\d|20\d\d)\b', cleaned)
    if m3:
        return f"{m3.group(1)}-01"
        
    return cleaned


def extract_dates_and_clean_header(header_line: str) -> Tuple[Optional[str], Optional[str], bool, str]:
    """
    Extracts start date, end date, current flag, and the header line with dates removed.
    """
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    
    match = DATE_RANGE_REGEX.search(header_line)
    if match:
        start_raw = match.group("start")
        end_raw = match.group("end")
        start_date = normalize_date(start_raw)
        if end_raw.lower() in ("present", "current"):
            is_current = True
            end_date = None
        else:
            end_date = normalize_date(end_raw)
            
        cleaned_header = header_line[:match.start()] + header_line[match.end():]
        cleaned_header = cleaned_header.strip(" -–—\t")
        return start_date, end_date, is_current, cleaned_header
        
    # Single date or "Present"
    if "present" in header_line.lower() or "current" in header_line.lower():
        is_current = True
        
    return start_date, end_date, is_current, header_line


def parse_experience_header(header_line: str) -> Tuple[str, str, Optional[str], Optional[str], Optional[str], bool]:
    """
    Parses title, company, location, start, end, current from experience header string.
    Ensures multiword companies like 'Handshake AI', 'Google Developer Student Club',
    'The University of Texas at Dallas' are preserved intact.
    """
    start_date, end_date, is_current, cleaned = extract_dates_and_clean_header(header_line)
    
    location: Optional[str] = None
    # Check for [Location] or (Location) e.g., "Instructor - iCode [North Dallas]"
    loc_match = LOCATION_BRACKET_REGEX.search(cleaned)
    if loc_match:
        location = (loc_match.group(1) or loc_match.group(2)).strip()
        cleaned = cleaned[:loc_match.start()] + cleaned[loc_match.end():]
        cleaned = cleaned.strip(" -–—,\t")

    title = ""
    company = ""
    
    # Pattern: Title - Company or Company - Title
    if " - " in cleaned or " – " in cleaned or " — " in cleaned:
        parts = re.split(r'\s+[-–—]\s+', cleaned, maxsplit=1)
        # Check known title keywords vs company patterns
        left = parts[0].strip()
        right = parts[1].strip()
        
        # Check if right has a location comma: e.g. "Google, Austin, TX"
        if ", " in right and not location:
            subparts = right.split(", ", 1)
            right = subparts[0].strip()
            location = subparts[1].strip()
            
        title = left
        company = right
    elif " | " in cleaned:
        parts = cleaned.split(" | ", 1)
        title = parts[0].strip()
        company = parts[1].strip()
    elif ", " in cleaned:
        parts = cleaned.split(", ")
        if len(parts) >= 2:
            title = parts[0].strip()
            company = parts[1].strip()
            if len(parts) > 2 and not location:
                location = ", ".join(parts[2:]).strip()
    else:
        title = cleaned
        company = cleaned

    return title, company, location, start_date, end_date, is_current


def build_experience_item(
    header_line: str,
    bullets: List[str]
) -> ExperienceItem:
    title, company, location, start, end, current = parse_experience_header(header_line)
    
    return ExperienceItem(
        title=FieldWithMeta(value=title, confidence=0.95, source_span=header_line),
        company=FieldWithMeta(value=company, confidence=0.95, source_span=header_line),
        location=FieldWithMeta(
            value=location,
            confidence=0.95 if location else 1.0,
            source_span=header_line if location else None,
            flag=None if location else "empty_in_resume"
        ),
        start=FieldWithMeta(value=start, confidence=0.95 if start else 0.5, source_span=header_line),
        end=FieldWithMeta(
            value=end,
            confidence=0.95 if (end or current) else 0.5,
            source_span=header_line,
            flag="current_job" if current else (None if end else "empty_in_resume")
        ),
        current=FieldWithMeta(value=current, confidence=0.95),
        bullets=FieldWithMeta(value=bullets, confidence=0.95)
    )
