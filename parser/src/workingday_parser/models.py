from enum import Enum
from typing import Generic, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class DegreeCanonical(str, Enum):
    ASSOCIATES = "Associate's"
    BACHELORS = "Bachelor's"
    MASTERS = "Master's"
    DOCTORATE = "Doctorate"
    HIGH_SCHOOL = "High School"
    CERTIFICATE = "Certificate"
    OTHER = "Other"


class NamingConvention(str, Enum):
    GIVEN_FIRST = "given-first"
    FAMILY_FIRST = "family-first"
    TWO_SURNAME = "two-surname"
    PATRONYMIC = "patronymic"
    MONONYM = "mononym"
    CAPS_SURNAME = "caps-surname"
    LAST_FIRST = "Last, First"
    UNKNOWN = "unknown"


class FieldWithMeta(BaseModel, Generic[T]):
    value: Optional[T] = None
    confidence: float = 1.0  # 0.0 to 1.0
    source_span: Optional[str] = None
    flag: Optional[str] = None  # e.g., "low_confidence", "empty_in_resume", "ambiguous"

    def is_empty(self) -> bool:
        return self.value is None or (isinstance(self.value, str) and not self.value.strip())


class NameCandidate(BaseModel):
    given: str
    family: str
    middle: Optional[str] = None
    description: str
    is_primary: bool = False


class NameModel(BaseModel):
    given: FieldWithMeta[str]
    family: FieldWithMeta[str]
    middle: FieldWithMeta[Optional[str]]
    convention: NamingConvention = NamingConvention.GIVEN_FIRST
    candidate_parses: List[NameCandidate] = []


class AddressModel(BaseModel):
    line1: FieldWithMeta[Optional[str]] = Field(
        default_factory=lambda: FieldWithMeta(value=None, confidence=1.0, flag="empty_in_resume")
    )
    line2: FieldWithMeta[Optional[str]] = Field(
        default_factory=lambda: FieldWithMeta(value=None, confidence=1.0, flag="empty_in_resume")
    )
    city: FieldWithMeta[Optional[str]] = Field(
        default_factory=lambda: FieldWithMeta(value=None, confidence=1.0)
    )
    state: FieldWithMeta[Optional[str]] = Field(
        default_factory=lambda: FieldWithMeta(value=None, confidence=1.0)
    )
    postal: FieldWithMeta[Optional[str]] = Field(
        default_factory=lambda: FieldWithMeta(value=None, confidence=1.0)
    )
    country: FieldWithMeta[Optional[str]] = Field(
        default_factory=lambda: FieldWithMeta(value="United States", confidence=0.9)
    )


class LinksModel(BaseModel):
    linkedin: FieldWithMeta[Optional[str]] = Field(
        default_factory=lambda: FieldWithMeta(value=None)
    )
    github: FieldWithMeta[Optional[str]] = Field(
        default_factory=lambda: FieldWithMeta(value=None)
    )
    websites: FieldWithMeta[List[str]] = Field(
        default_factory=lambda: FieldWithMeta(value=[])
    )


class EducationItem(BaseModel):
    school: FieldWithMeta[str]
    degree: FieldWithMeta[Optional[DegreeCanonical]]
    degree_raw: FieldWithMeta[Optional[str]] = Field(default_factory=lambda: FieldWithMeta(value=None))
    field: FieldWithMeta[Optional[str]] = Field(default_factory=lambda: FieldWithMeta(value=None))
    minor: FieldWithMeta[Optional[str]] = Field(default_factory=lambda: FieldWithMeta(value=None))
    start: FieldWithMeta[Optional[str]] = Field(default_factory=lambda: FieldWithMeta(value=None, flag="empty_in_resume"))  # YYYY-MM or null
    end: FieldWithMeta[Optional[str]] = Field(default_factory=lambda: FieldWithMeta(value=None))    # YYYY-MM or null
    gpa: FieldWithMeta[Optional[str]] = Field(default_factory=lambda: FieldWithMeta(value=None, flag="empty_in_resume"))


class ExperienceItem(BaseModel):
    title: FieldWithMeta[str]
    company: FieldWithMeta[str]
    location: FieldWithMeta[Optional[str]] = Field(default_factory=lambda: FieldWithMeta(value=None))
    start: FieldWithMeta[Optional[str]] = Field(default_factory=lambda: FieldWithMeta(value=None))  # YYYY-MM
    end: FieldWithMeta[Optional[str]] = Field(default_factory=lambda: FieldWithMeta(value=None))    # YYYY-MM or null if current
    current: FieldWithMeta[bool] = Field(default_factory=lambda: FieldWithMeta(value=False))
    bullets: FieldWithMeta[List[str]] = Field(default_factory=lambda: FieldWithMeta(value=[]))


class ProjectItem(BaseModel):
    name: FieldWithMeta[str]
    category: FieldWithMeta[Optional[str]] = Field(default_factory=lambda: FieldWithMeta(value=None)) # e.g. "Personal Project", "Group Project"
    bullets: FieldWithMeta[List[str]] = Field(default_factory=lambda: FieldWithMeta(value=[]))
    technologies: FieldWithMeta[List[str]] = Field(default_factory=lambda: FieldWithMeta(value=[]))
    link: FieldWithMeta[Optional[str]] = Field(default_factory=lambda: FieldWithMeta(value=None))


class ResumeData(BaseModel):
    name: NameModel
    email: FieldWithMeta[Optional[str]]
    phone: FieldWithMeta[Optional[str]]
    address: AddressModel
    links: LinksModel
    education: List[EducationItem] = []
    experience: List[ExperienceItem] = []
    projects: List[ProjectItem] = []
    skills: Dict[str, List[str]] = {}
    raw_text: Optional[str] = None
    warnings: List[str] = []
