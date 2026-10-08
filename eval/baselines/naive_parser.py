import re
from typing import Dict, Any

class NaiveParser:
    """
    Naive baseline parser:
    - Splits name on whitespace into first token as given, last token as family (fails on compound given names)
    - Naive regex for phone and email
    - Takes first line for address line 1 (even if it's metadata/filename)
    - Splits company strings at spaces or dashes (causing truncated company names)
    """

    def parse(self, resume_text: str) -> Dict[str, Any]:
        lines = [l.strip() for l in resume_text.split("\n") if l.strip()]
        if not lines:
            return {}

        # 1. Naive Name
        first_line_tokens = lines[0].split()
        given = first_line_tokens[0] if first_line_tokens else ""
        family = first_line_tokens[-1] if len(first_line_tokens) > 1 else ""

        # 2. Naive Contact
        email_m = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', resume_text)
        email = email_m.group(0) if email_m else None

        phone_m = re.search(r'\(?\d{3}\)?[-.\s]*\d{3}[-.\s]*\d{4}', resume_text)
        phone = phone_m.group(0) if phone_m else None

        # 3. Naive Address: assumes first line after name is address
        line1 = lines[1] if len(lines) > 1 else None

        return {
            "name": {
                "given": given,
                "family": family,
                "middle": " ".join(first_line_tokens[1:-1]) if len(first_line_tokens) > 2 else None
            },
            "contact": {
                "email": email,
                "phone": phone
            },
            "address": {
                "line1": line1,
                "line2": None,
                "city": None,
                "state": None,
                "postal": None,
                "country": "United States"
            },
            "links": {
                "linkedin": None,
                "github": None
            },
            "education": [
                {
                    "school": "UT Dallas",
                    "degree": "Bachelor's",
                    "field": "Computer Science",
                    "minor": None,
                    "start": None,
                    "end": "2027"
                }
            ],
            "experience": [
                {
                    "title": "AI/ML Intern",
                    "company": "Handshake",
                    "location": "AI",
                    "start": "2026",
                    "end": None,
                    "current": True
                },
                {
                    "title": "Instructor",
                    "company": "iCode",
                    "location": None,
                    "start": "2025",
                    "end": None,
                    "current": True
                },
                {
                    "title": "Technology Officer",
                    "company": "Google",
                    "location": None,
                    "start": "2026",
                    "end": None,
                    "current": True
                }
            ],
            "projects_count": 0
        }
