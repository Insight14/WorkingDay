import re
from typing import Optional, Tuple
from ..models import EducationItem, DegreeCanonical, FieldWithMeta
from .experience import normalize_date, DATE_RANGE_REGEX

DEGREE_MAPPINGS = [
    (r"\b(bachelor'?s?|bs|ba|b\.s\.|b\.a\.|b\.tech|btech|b\.e\.|undergraduate)\b", DegreeCanonical.BACHELORS),
    (r"\b(master'?s?|ms|ma|m\.s\.|m\.a\.|m\.tech|mtech|m\.e\.|graduate|mba)\b", DegreeCanonical.MASTERS),
    (r"\b(ph\.?d\.?|doctorate|doctor of philosophy)\b", DegreeCanonical.DOCTORATE),
    (r"\b(associate'?s?|aa|as|a\.a\.|a\.s\.)\b", DegreeCanonical.ASSOCIATES),
    (r"\b(high school|diploma|secondary school)\b", DegreeCanonical.HIGH_SCHOOL),
    (r"\b(certificate|certification|bootcamp)\b", DegreeCanonical.CERTIFICATE),
]

def map_degree_canonical(text: str) -> Optional[DegreeCanonical]:
    text_lower = text.lower()
    for pattern, canonical in DEGREE_MAPPINGS:
        if re.search(pattern, text_lower):
            return canonical
    return DegreeCanonical.OTHER


def parse_degree_and_majors(raw_text: str) -> Tuple[Optional[DegreeCanonical], Optional[str], Optional[str], Optional[str]]:
    # Remove dates from raw_text first
    text_clean = DATE_RANGE_REGEX.sub('', raw_text)
    text_clean = re.sub(r'\b(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?(20\d\d|19\d\d)\b', '', text_clean).strip()

    canonical_degree = map_degree_canonical(text_clean)
    
    minor_val: Optional[str] = None
    minor_match = re.search(r'(?:\+|\bwith\b|,)?\s*Minor\s*(?:in|:)?\s*([^,\n–—-]+)', text_clean, re.IGNORECASE)
    cleaned_maj = text_clean
    if minor_match:
        minor_val = minor_match.group(1).strip()
        cleaned_maj = text_clean[:minor_match.start()] + text_clean[minor_match.end():]

    field_val: Optional[str] = None
    field_match = re.search(r'(?:in|of)\s+([A-Za-z\s&/.-]+)', cleaned_maj, re.IGNORECASE)
    if field_match:
        field_val = field_match.group(1).strip()
        field_val = re.sub(r'^(Degree|Science|Arts)\s+in\s+', '', field_val, flags=re.IGNORECASE)
        field_val = re.sub(r'[,.\s]+$', '', field_val)
    elif canonical_degree and canonical_degree != DegreeCanonical.OTHER:
        for pattern, _ in DEGREE_MAPPINGS:
            m = re.search(pattern, cleaned_maj, re.IGNORECASE)
            if m:
                after = cleaned_maj[m.end():].strip(" ,-–—:")
                if after:
                    field_val = after
                break

    return canonical_degree, raw_text.strip(), field_val, minor_val


def parse_education_block(
    header_line: str,
    details_line: Optional[str] = None,
    gpa: Optional[str] = None
) -> EducationItem:
    combined = f"{header_line} {details_line or ''}".strip()
    
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    range_match = DATE_RANGE_REGEX.search(combined)
    if range_match:
        start_date = normalize_date(range_match.group("start"))
        end_date = normalize_date(range_match.group("end"))
        combined_no_date = combined[:range_match.start()] + combined[range_match.end():]
    else:
        single_date_match = re.search(r'\b(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?(20\d\d|19\d\d)\b', combined)
        if single_date_match:
            end_date = normalize_date(single_date_match.group(0))
            combined_no_date = combined[:single_date_match.start()] + combined[single_date_match.end():]
        else:
            combined_no_date = combined

    school_name = ""
    degree_text = ""
    
    dash_split = re.split(r'\s*[-–—]\s*(?=[A-Z])', header_line, maxsplit=1)
    if len(dash_split) == 2:
        school_name = dash_split[0].strip()
        degree_text = dash_split[1].strip()
    else:
        degree_found = False
        for pattern, _ in DEGREE_MAPPINGS:
            deg_m = re.search(pattern, header_line, re.IGNORECASE)
            if deg_m and deg_m.start() > 0:
                school_name = header_line[:deg_m.start()].rstrip(" -–—,:\t")
                degree_text = header_line[deg_m.start():].strip()
                degree_found = True
                break
        if not degree_found:
            school_name = header_line.strip()
            degree_text = details_line or ""

    canonical, raw_deg, field, minor = parse_degree_and_majors(degree_text or combined_no_date)

    if not gpa:
        gpa_match = re.search(r'GPA:?\s*(\d\.\d+(?:/\d\.\d+)?)', combined, re.IGNORECASE)
        if gpa_match:
            gpa = gpa_match.group(1)

    return EducationItem(
        school=FieldWithMeta(value=school_name, confidence=0.98, source_span=header_line),
        degree=FieldWithMeta(value=canonical, confidence=0.95 if canonical else 0.5),
        degree_raw=FieldWithMeta(value=raw_deg, confidence=0.9),
        field=FieldWithMeta(value=field, confidence=0.95 if field else 0.5),
        minor=FieldWithMeta(
            value=minor, 
            confidence=0.95 if minor else 1.0, 
            flag=None if minor else "empty_in_resume"
        ),
        start=FieldWithMeta(
            value=start_date, 
            confidence=0.95 if start_date else 1.0,
            flag=None if start_date else "empty_in_resume"
        ),
        end=FieldWithMeta(
            value=end_date, 
            confidence=0.95 if end_date else 0.5
        ),
        gpa=FieldWithMeta(
            value=gpa, 
            confidence=0.95 if gpa else 1.0,
            flag=None if gpa else "empty_in_resume"
        )
    )
