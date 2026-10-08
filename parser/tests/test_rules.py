import pytest
from workingday_parser.rules.name import parse_name, detect_naming_convention
from workingday_parser.rules.address import parse_address_block
from workingday_parser.rules.experience import parse_experience_header, build_experience_item
from workingday_parser.rules.education import parse_education_block, map_degree_canonical, parse_degree_and_majors
from workingday_parser.rules.links import extract_links_from_text_and_uris, normalize_url
from workingday_parser.models import DegreeCanonical, NamingConvention
from workingday_parser.ingest.bullets import rebuild_bullet_list, rejoin_hyphenation

class TestNameRules:
    def test_sri_satya_sourish_reddy_default(self):
        result = parse_name(
            raw_name="Sri Satya Sourish Reddy",
            email="reddysourish@gmail.com",
            linkedin_url="https://linkedin.com/in/sri-satya-sourish-reddy/",
            put_additional_given_in_middle=False
        )
        assert result.given.value == "Sri Satya Sourish"
        assert result.family.value == "Reddy"
        assert result.middle.value is None
        assert len(result.candidate_parses) >= 2

    def test_sri_satya_sourish_reddy_middle_toggle(self):
        result = parse_name(
            raw_name="Sri Satya Sourish Reddy",
            email="reddysourish@gmail.com",
            linkedin_url="https://linkedin.com/in/sri-satya-sourish-reddy/",
            put_additional_given_in_middle=True
        )
        assert result.given.value == "Sri"
        assert result.middle.value == "Satya Sourish"
        assert result.family.value == "Reddy"

    def test_particle_names(self):
        result = parse_name("Ludwig van Beethoven")
        assert result.given.value == "Ludwig"
        assert result.family.value == "van Beethoven"

    def test_last_first_format(self):
        result = parse_name("Reddy, Sri Satya Sourish")
        assert result.convention == NamingConvention.LAST_FIRST
        assert result.family.value == "Reddy"
        assert result.given.value == "Sri Satya Sourish"


class TestAddressRules:
    def test_header_without_street(self):
        raw = "Plano, TX 75025 | (469)-970-9045 | reddysourish@gmail.com"
        addr = parse_address_block(raw)
        assert addr.line1.value is None
        assert addr.line1.flag == "empty_in_resume"
        assert addr.city.value == "Plano"
        assert addr.state.value == "TX"
        assert addr.postal.value == "75025"
        assert addr.country.value == "United States"

    def test_address_with_line2_apt(self):
        raw = "123 Main St, Apt # 1234, Plano, TX 75025"
        addr = parse_address_block(raw)
        assert addr.line1.value == "123 Main St"
        assert addr.line2.value == "Apt # 1234"
        assert addr.city.value == "Plano"
        assert addr.state.value == "TX"
        assert addr.postal.value == "75025"

    def test_address_with_building_block(self):
        raw = "Building/Block # 123, Seattle, WA 98101"
        addr = parse_address_block(raw)
        assert addr.line1.value is None  # no street
        assert "Block # 123" in addr.line2.value or "# 123" in addr.line2.value
        assert addr.city.value == "Seattle"
        assert addr.state.value == "WA"
        assert addr.postal.value == "98101"


class TestExperienceRules:
    def test_handshake_ai_intern(self):
        header = "AI/ML Intern - Handshake AI May 2026 - Present"
        title, company, loc, start, end, current = parse_experience_header(header)
        assert title == "AI/ML Intern"
        assert company == "Handshake AI"
        assert loc is None
        assert start == "2026-05"
        assert end is None
        assert current is True

    def test_icode_with_bracket_location(self):
        header = "Instructor - iCode [North Dallas] October 2025 - Present"
        title, company, loc, start, end, current = parse_experience_header(header)
        assert title == "Instructor"
        assert company == "iCode"
        assert loc == "North Dallas"
        assert start == "2025-10"
        assert current is True

    def test_google_developer_student_club_intact(self):
        header = "Technology Officer & Project Mentor - Google Developer Student Club Jan 2026 - Present"
        title, company, loc, start, end, current = parse_experience_header(header)
        assert title == "Technology Officer & Project Mentor"
        assert company == "Google Developer Student Club"
        assert current is True

    def test_ut_dallas_research_assistant(self):
        header = "Undergraduate Research Assistant - The University of Texas at Dallas August 2026 - Present"
        title, company, loc, start, end, current = parse_experience_header(header)
        assert title == "Undergraduate Research Assistant"
        assert company == "The University of Texas at Dallas"
        assert current is True


class TestEducationRules:
    def test_ut_dallas_degree_and_minor(self):
        header = "The University of Texas at Dallas- Bachelor's in Computer Science + Minor in Data Science & A.I December 2027"
        item = parse_education_block(header)
        assert "University of Texas at Dallas" in item.school.value
        assert item.degree.value == DegreeCanonical.BACHELORS
        assert item.field.value == "Computer Science"
        assert item.minor.value == "Data Science & A.I"
        assert item.end.value == "2027-12"
        assert item.start.value is None
        assert item.start.flag == "empty_in_resume"


class TestLinksRules:
    def test_glued_urls_and_normalization(self):
        raw = "linkedin.com/in/sri-satya-sourish-reddy/ |github.com/Insight14"
        links = extract_links_from_text_and_uris(raw)
        assert links.linkedin.value == "https://linkedin.com/in/sri-satya-sourish-reddy/"
        assert links.github.value == "https://github.com/Insight14"
        assert "https://github.com/Insight14" in links.websites.value


class TestBulletRebuilding:
    def test_bullet_line_wraps_and_hyphenation(self):
        raw_lines = [
            "• Created 50+ challenging software engineering benchmarks, golden solutions, and automated test cases using Python, JavaScript, C++,",
            "Docker, and Git to evaluate LLM performance across coding, debugging, and system design tasks.",
            "• Identified critical model failure modes through adversarial test development, helping improve AI evaluation frameworks and benchmark",
            "reliability for next-generation coding assistants."
        ]
        bullets = rebuild_bullet_list(raw_lines)
        assert len(bullets) == 2
        assert "Docker, and Git to evaluate LLM performance" in bullets[0]
        assert "reliability for next-generation coding assistants." in bullets[1]

    def test_portfolio_ready_hyphenation(self):
        raw_lines = [
            "• Led interactive projects, coding exercises, and hands-on labs that increased student engagement by 35%, helping students build portfolio-",
            "ready projects, and gain practical experience with software development, data analysis, and cybersecurity tools."
        ]
        bullets = rebuild_bullet_list(raw_lines)
        assert len(bullets) == 1
        assert "portfolio-ready" in bullets[0]
