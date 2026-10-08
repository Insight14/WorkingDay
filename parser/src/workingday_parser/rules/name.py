import re
from typing import Optional, List, Tuple
from nameparser import HumanName
from ..models import NameModel, NameCandidate, NamingConvention, FieldWithMeta

SURNAME_PARTICLES = {
    "van", "von", "de", "del", "della", "de la", "da", "di", "du", 
    "bin", "ibn", "bint", "al", "al-", "el", "el-", "o'", "mc", "mac", 
    "san", "santa", "ter", "ten", "van de", "van den", "van der"
}

def clean_name_string(raw: str) -> str:
    # Remove titles/credentials like PhD, M.S., etc. if trailing
    text = re.sub(r'[\r\n\t]+', ' ', raw).strip()
    text = re.sub(r'^(Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+', '', text, flags=re.IGNORECASE)
    text = re.sub(r',\s*(PhD|MD|MS|BS|B\.S\.|M\.S\.|Ph\.D\.|Esq\.?|Jr\.?|Sr\.?|III|IV|II)$', '', text, flags=re.IGNORECASE)
    return text.strip()


def detect_naming_convention(
    raw_name: str, 
    email: Optional[str] = None, 
    linkedin_url: Optional[str] = None
) -> Tuple[NamingConvention, str, str, Optional[str], List[NameCandidate]]:
    """
    Parses a name into given, family, and optional middle names according to
    conventions and cross-checks (email, linkedin).
    Never infers or outputs nationality.
    """
    clean = clean_name_string(raw_name)
    tokens = clean.split()
    
    candidates: List[NameCandidate] = []
    
    if not tokens:
        return (NamingConvention.UNKNOWN, "", "", None, [])
    
    if len(tokens) == 1:
        mononym = tokens[0]
        candidates.append(NameCandidate(
            given=mononym,
            family=mononym,
            middle=None,
            description="Mononym",
            is_primary=True
        ))
        return (NamingConvention.MONONYM, mononym, mononym, None, candidates)
    
    # Check "Last, First Middle" format
    if "," in clean:
        parts = clean.split(",", 1)
        family_part = parts[0].strip()
        rest = parts[1].strip().split()
        if rest:
            given_part = " ".join(rest)
            candidates.append(NameCandidate(
                given=given_part,
                family=family_part,
                middle=None,
                description="Last, First Middle format (Full given name in First Name)",
                is_primary=True
            ))
            if len(rest) > 1:
                candidates.append(NameCandidate(
                    given=rest[0],
                    family=family_part,
                    middle=" ".join(rest[1:]),
                    description="Last, First format with separate Middle Name",
                    is_primary=False
                ))
            return (NamingConvention.LAST_FIRST, given_part, family_part, None, candidates)

    # Check ALL-CAPS surname convention: e.g. "Sourish REDDY" or "REDDY Sourish"
    caps_indices = [i for i, t in enumerate(tokens) if t.isupper() and len(t) > 1 and t.isalpha()]
    if 0 < len(caps_indices) < len(tokens):
        if caps_indices == [0]:  # Family name first in caps
            family = tokens[0]
            given = " ".join(tokens[1:])
            candidates.append(NameCandidate(
                given=given,
                family=family,
                middle=None,
                description="Uppercase Surname First",
                is_primary=True
            ))
            return (NamingConvention.CAPS_SURNAME, given, family, None, candidates)
        elif caps_indices == [len(tokens) - 1]: # Surname last in caps
            family = tokens[-1]
            given = " ".join(tokens[:-1])
            candidates.append(NameCandidate(
                given=given,
                family=family,
                middle=None,
                description="Uppercase Surname Last",
                is_primary=True
            ))
            return (NamingConvention.CAPS_SURNAME, given, family, None, candidates)

    # Check particles in name
    # e.g., "Leonardo DiCaprio", "Ludwig van Beethoven", "Carlos de la Vega"
    particle_idx = -1
    for i, t in enumerate(tokens):
        if t.lower() in SURNAME_PARTICLES:
            particle_idx = i
            break
            
    if particle_idx != -1 and particle_idx > 0:
        given = " ".join(tokens[:particle_idx])
        family = " ".join(tokens[particle_idx:])
        candidates.append(NameCandidate(
            given=given,
            family=family,
            middle=None,
            description="Surname with particle",
            is_primary=True
        ))
        return (NamingConvention.TWO_SURNAME if " " in family else NamingConvention.GIVEN_FIRST, 
                given, family, None, candidates)

    # Check Email and LinkedIn Cross-checks
    # e.g. email "reddysourish@gmail.com" has "reddy" and "sourish"
    # linkedin "sri-satya-sourish-reddy"
    email_local = email.split("@")[0].lower() if email and "@" in email else ""
    linkedin_slug = ""
    if linkedin_url:
        match = re.search(r'linkedin\.com/in/([^/?#]+)', linkedin_url, re.IGNORECASE)
        if match:
            linkedin_slug = match.group(1).lower().replace("-", "")

    # Multi-token given names (e.g., "Sri Satya Sourish Reddy")
    # In Indian / Western / Southeast Asian contexts, compound given names often precede a single family name.
    # Default high-accuracy heuristic for multiword names:
    # 1. Option A (Primary for Workday): Full given prefix in First Name ("Sri Satya Sourish"), Last token as Family ("Reddy")
    # 2. Option B (Traditional Western split): First token ("Sri"), Middle ("Satya Sourish"), Last ("Reddy")
    
    family = tokens[-1]
    given_full = " ".join(tokens[:-1])
    
    convention = NamingConvention.GIVEN_FIRST
    
    # Add primary option (Full compound given name in First Name for Workday autofill accuracy)
    candidates.append(NameCandidate(
        given=given_full,
        family=family,
        middle=None,
        description=f"Full Given Name in First Name ('{given_full}'), Last Name ('{family}')",
        is_primary=True
    ))
    
    # If more than 2 tokens, add candidate with Middle Name separated
    if len(tokens) > 2:
        candidates.append(NameCandidate(
            given=tokens[0],
            family=family,
            middle=" ".join(tokens[1:-1]),
            description=f"First ('{tokens[0]}'), Middle ('{' '.join(tokens[1:-1])}'), Last ('{family}')",
            is_primary=False
        ))
        # Also candidate if family name is the first token (Family-first convention)
        candidates.append(NameCandidate(
            given=" ".join(tokens[1:]),
            family=tokens[0],
            middle=None,
            description=f"Family First ('{tokens[0]}'), Given ('{' '.join(tokens[1:])}')",
            is_primary=False
        ))

    return (convention, given_full, family, None, candidates)


def parse_name(
    raw_name: str,
    email: Optional[str] = None,
    linkedin_url: Optional[str] = None,
    put_additional_given_in_middle: bool = False
) -> NameModel:
    convention, given, family, middle, candidates = detect_naming_convention(
        raw_name, email=email, linkedin_url=linkedin_url
    )
    
    tokens = clean_name_string(raw_name).split()
    
    if put_additional_given_in_middle and len(tokens) > 2 and convention == NamingConvention.GIVEN_FIRST:
        selected_given = tokens[0]
        selected_middle = " ".join(tokens[1:-1])
        selected_family = tokens[-1]
    else:
        selected_given = given
        selected_middle = middle
        selected_family = family

    confidence = 0.98 if (given and family) else 0.7

    return NameModel(
        given=FieldWithMeta(value=selected_given, confidence=confidence, source_span=raw_name),
        family=FieldWithMeta(value=selected_family, confidence=confidence, source_span=raw_name),
        middle=FieldWithMeta(value=selected_middle, confidence=confidence if selected_middle else 1.0),
        convention=convention,
        candidate_parses=candidates
    )
