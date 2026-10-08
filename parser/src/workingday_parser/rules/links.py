import re
from typing import List, Optional
from ..models import LinksModel, FieldWithMeta

URL_REGEX = re.compile(
    r'(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s|]*)?)',
    re.IGNORECASE
)

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'(?:\+?1[-.\s]*)?\(?\d{3}\)?[-.\s]*\d{3}[-.\s]*\d{4}')

def normalize_url(url: str) -> str:
    cleaned = url.strip().strip("| \t\r\n")
    cleaned = re.sub(r'^[|/\s]+', '', cleaned)
    if not cleaned.startswith("http://") and not cleaned.startswith("https://"):
        cleaned = "https://" + cleaned
    return cleaned


def extract_links_from_text_and_uris(
    text: str,
    annotation_uris: Optional[List[str]] = None
) -> LinksModel:
    all_uris: List[str] = []
    
    if annotation_uris:
        for uri in annotation_uris:
            if uri:
                all_uris.append(uri.strip())

    text_no_email = EMAIL_REGEX.sub('', text)
    matches = URL_REGEX.findall(text_no_email)
    for m in matches:
        if "." in m and not m.endswith((".png", ".jpg", ".jpeg", ".pdf", ".txt")):
            all_uris.append(m)

    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    other_websites: List[str] = []
    
    seen = set()
    for raw_u in all_uris:
        norm = normalize_url(raw_u)
        if norm.lower() in seen:
            continue
        seen.add(norm.lower())

        if "linkedin.com" in norm.lower():
            if not linkedin_url:
                linkedin_url = norm
        elif "github.com" in norm.lower():
            if not github_url:
                github_url = norm
                other_websites.append(norm)
        else:
            other_websites.append(norm)

    return LinksModel(
        linkedin=FieldWithMeta(
            value=linkedin_url,
            confidence=0.98 if linkedin_url else 1.0,
            flag=None if linkedin_url else "empty_in_resume"
        ),
        github=FieldWithMeta(
            value=github_url,
            confidence=0.98 if github_url else 1.0,
            flag=None if github_url else "empty_in_resume"
        ),
        websites=FieldWithMeta(
            value=other_websites,
            confidence=0.95
        )
    )


def extract_contact_info(text: str) -> tuple[Optional[str], Optional[str]]:
    email_match = EMAIL_REGEX.search(text)
    email = email_match.group(0).strip() if email_match else None
    
    phone_match = PHONE_REGEX.search(text)
    phone = phone_match.group(0).strip() if phone_match else None
    
    return email, phone
