import re
from typing import Optional
from ..models import AddressModel, FieldWithMeta

US_STATE_ABBREVIATIONS = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"
}

STATE_NAMES_TO_ABBR = {
    "texas": "TX", "california": "CA", "new york": "NY", "washington": "WA",
    "florida": "FL", "illinois": "IL", "massachusetts": "MA", "georgia": "GA",
    "colorado": "CO", "virginia": "VA", "north carolina": "NC", "ohio": "OH",
    "pennsylvania": "PA", "michigan": "MI", "arizona": "AZ", "new jersey": "NJ"
}

ADDR2_REGEX = re.compile(
    r'(?:(?:Building/Block|Block/Building|Building\s*#|Block\s*#|Apt|Apartment|Unit|Suite|Ste|Bldg|Building|Block|Floor|Fl|Room)\.?\s*(?:#|No\.?|Number)?\s*[A-Za-z0-9-]+|#\s*[A-Za-z0-9-]+)',
    re.IGNORECASE
)

STREET_INDICATORS = re.compile(
    r'\b(?:\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way|Parkway|Pkwy|Plaza|Pl))\b',
    re.IGNORECASE
)

def parse_address_block(raw_text: str) -> AddressModel:
    if not raw_text or not raw_text.strip():
        return AddressModel()

    # If raw_text contains multiple lines, find the line containing city/state/address cues
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    addr_line = lines[0]
    for line in lines:
        if any(f" {st}" in line or f", {st}" in line or f",{st}" in line for st in US_STATE_ABBREVIATIONS) or re.search(r'\b\d{5}\b', line):
            addr_line = line
            break

    # Strip pipe segments if email/phone are on same line
    parts = [p.strip() for p in addr_line.split("|")]
    addr_candidate = parts[0]
    for p in parts:
        if any(f" {st}" in p or f", {st}" in p for st in US_STATE_ABBREVIATIONS) or re.search(r'\b\d{5}\b', p):
            addr_candidate = p
            break

    source_span = addr_candidate

    line2_val: Optional[str] = None
    line2_match = ADDR2_REGEX.search(addr_candidate)
    if line2_match:
        line2_val = line2_match.group(0).strip()
        addr_candidate = addr_candidate[:line2_match.start()] + " " + addr_candidate[line2_match.end():]

    line1_val: Optional[str] = None
    street_match = STREET_INDICATORS.search(addr_candidate)
    if street_match:
        line1_val = street_match.group(0).strip()
        addr_candidate = addr_candidate[:street_match.start()] + " " + addr_candidate[street_match.end():]

    # Clean residual punctuation, slashes, commas
    addr_candidate = re.sub(r'^[,\s/|]+|[,\s/|]+$', '', addr_candidate)
    addr_candidate = re.sub(r',\s*,+', ',', addr_candidate).strip()

    city_val: Optional[str] = None
    state_val: Optional[str] = None
    postal_val: Optional[str] = None

    match = re.search(r'([A-Za-z\s.]+),\s*([A-Za-z]{2,})\s*(\d{5}(?:-\d{4})?)?', addr_candidate)
    if match:
        city_candidate = match.group(1).strip(" ,./")
        # Ensure multi-line remnants aren't in city
        if "\n" in city_candidate:
            city_candidate = city_candidate.split("\n")[-1].strip()
        city_val = city_candidate if city_candidate else None

        st_candidate = match.group(2).strip().upper()
        if st_candidate in US_STATE_ABBREVIATIONS:
            state_val = st_candidate
        elif st_candidate.lower() in STATE_NAMES_TO_ABBR:
            state_val = STATE_NAMES_TO_ABBR[st_candidate.lower()]

        if match.group(3):
            postal_val = match.group(3).strip()
    else:
        match2 = re.search(r'([A-Za-z\s]+)\s+([A-Z]{2})\s+(\d{5})', addr_candidate)
        if match2:
            city_val = match2.group(1).strip(" ,./")
            state_val = match2.group(2).strip()
            postal_val = match2.group(3).strip()

    return AddressModel(
        line1=FieldWithMeta(
            value=line1_val,
            confidence=0.95 if line1_val else 1.0,
            source_span=source_span if line1_val else None,
            flag=None if line1_val else "empty_in_resume"
        ),
        line2=FieldWithMeta(
            value=line2_val,
            confidence=0.95 if line2_val else 1.0,
            source_span=source_span if line2_val else None,
            flag=None if line2_val else "empty_in_resume"
        ),
        city=FieldWithMeta(
            value=city_val,
            confidence=0.95 if city_val else 0.4,
            source_span=source_span
        ),
        state=FieldWithMeta(
            value=state_val,
            confidence=0.95 if state_val else 0.4,
            source_span=source_span
        ),
        postal=FieldWithMeta(
            value=postal_val,
            confidence=0.95 if postal_val else 0.4,
            source_span=source_span,
            flag=None if postal_val else "empty_in_resume"
        ),
        country=FieldWithMeta(
            value="United States" if (state_val in US_STATE_ABBREVIATIONS or postal_val) else "United States",
            confidence=0.95,
            source_span=source_span
        )
    )
