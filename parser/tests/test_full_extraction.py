import pytest
from workingday_parser.extract.extractor import WorkingDayExtractor
from workingday_parser.ingest.layout import TextBlock
from workingday_parser.models import DegreeCanonical

SAMPLE_RESUME_TEXT = """Sri Satya Sourish Reddy
Plano, TX 75025 | (469)-970-9045 | reddysourish@gmail.com
linkedin.com/in/sri-satya-sourish-reddy/ |github.com/Insight14

EDUCATION
The University of Texas at Dallas- Bachelor's in Computer Science + Minor in Data Science & A.I December 2027

TECHNICAL SKILLS
Front End | React.js, Next.js, Node.js, Vue, Angular, Swift, C#, Javascript, HTML/CSS, Figma
Back End | Python, Java, C++, R, SQL, Express.js, MongoDB, Firebase/FastAPI/Postman, AWS, REST APIs, Redis
Developer Tools| Git, Docker, npm, BeautifulSoap, LangGraph/LangChain, Agile/Scrum, Wireshark, Microsoft Office Suite
Coursework | Artificial Intelligence, Machine Learning, Computer Networks, Adv Algorithm Design & Analysis, Database Systems

EXPERIENCE
AI/ML Intern - Handshake AI May 2026 - Present
• Created 50+ challenging software engineering benchmarks, golden solutions, and automated test cases using Python, JavaScript, C++, Docker, and Git to evaluate LLM performance across coding, debugging, and system design tasks.
• Identified critical model failure modes through adversarial test development, helping improve AI evaluation frameworks and benchmark reliability for next-generation coding assistants.

Undergraduate Research Assistant - The University of Texas at Dallas August 2026 - Present
• Collaborating on development of an active electronically scanned array (AESA) antenna system for real-time UAV tracking, wireless communication, and power transfer.
• Contributing to control software and real-time data processing, collaborating across software, antenna, amplifier, and oscillator subsystems to support reliable UAV tracking.

Instructor - iCode [North Dallas] October 2025 - Present
• Teaching programming and technology concepts to 10+ students, covering Java, SQL, Python, Cybersecurity, and mentoring them through challenges to strengthen their technical skills and soft skills, problem-solving, collaboration, and critical thinking.
• Led interactive projects, coding exercises, and hands-on labs that increased student engagement by 35%, helping students build portfolio-ready projects, and gain practical experience with software development, data analysis, and cybersecurity tools.

Technology Officer & Project Mentor - Google Developer Student Club Jan 2026 - Present
• Mentoring 50+ students through a 10-week full-stack project, supporting architecture design, backend development, and integration of 3+ APIs/services such as React.js, FastAPI, Gemini, Express.js, Figma, nd REST APIs.
• Led weekly Scrum meetings and workshops (10+ meetings) to teach system design, deployment through git and Docker, Jira, and backend concepts, improving project completion readiness and presentation quality for final showcase.

PROJECTS
Project | Uber Stall Guard Personal Project
• Built a full-stack AI prototype (React, Leaflet.js, FastAPI, Python, scikit-learn) that detects rideshare driver-stalling behavior from GPS telemetry, training a calibrated RandomForest classifier on 1,200 synthetic trip samples across 8 scenarios, achieving ~97% accuracy (stable across multiple test splits) and 0.997 ROC-AUC on held-out data.
• Designed a tiered decision system, translating model confidence into automated rider protections (fee waiver, cancellation) using 5 engineered GPS features, with an interactive map-based demo with React and Google Maps SDK served via a FastAPI REST backend.

Project | 442ools Personal Project
• Built a YOLOv8 and ByteTrack football analytics pipeline using OpenCV, scikit-learn, and homography calibration to track players, goalkeepers, referees, and the ball with 98.4% precision, 88.4% recall, and 90.7% mAP@50.
• Implemented team classification, track-ID stabilization, pitch-coordinate mapping, and pass/shot/play suggestions across 1,055 video frames, exporting structured tracking and prediction data in JSONL format using a CVAT-labeled dataset.

Project | Vigorithm - Bridging healthcare and fitness Personal Project
• Architected a full-stack health-aware fitness platform using Next.js, TypeScript, FastAPI, PostgreSQL, and Claude API to generate personalized workout and diet plans based on health conditions, injuries, and body goals.
• Built a LangChain/pgvector RAG pipeline to ground AI-generated routines in uploaded medical documents, with a phased architecture separating recommendations from a planned MediaPipe form-correction module for scalability.

Project | CoDriver - Association of Machinery and Computing (ACM UTD) Group Project
• Built a 100% voice-activated AI mobile driving assistant using React Native, integrating 5+ RESTful APIs (Claude, ElevenLabs, Spotify, Google Maps, OpenWeather) for hands-free navigation, music control, and route recommendations.
• Developed full-stack architecture with Node.js, Express.js, and MongoDB, managing user authentication, preferences, and chat history, resulting in a 35% decrease in drowsy driving and car crashes.
"""

def test_full_resume_pipeline():
    extractor = WorkingDayExtractor()
    lines = [l for l in SAMPLE_RESUME_TEXT.split("\n") if l.strip()]
    
    # Text blocks partitioned by headings
    blocks = [
        TextBlock(lines=[lines[0], lines[1], lines[2]], bbox=(0, 0, 500, 60)),
        TextBlock(lines=["EDUCATION"], bbox=(0, 70, 500, 90)),
        TextBlock(lines=[lines[4]], bbox=(0, 95, 500, 120)),
        TextBlock(lines=["TECHNICAL SKILLS"], bbox=(0, 130, 500, 150)),
        TextBlock(lines=lines[6:10], bbox=(0, 155, 500, 220)),
        TextBlock(lines=["EXPERIENCE"], bbox=(0, 230, 500, 250)),
        TextBlock(lines=lines[11:23], bbox=(0, 255, 500, 500)),
        TextBlock(lines=["PROJECTS"], bbox=(0, 510, 500, 530)),
        TextBlock(lines=lines[24:], bbox=(0, 535, 500, 900)),
    ]
    
    data = extractor.extract_from_blocks(blocks)
    
    # 1. Name checks
    assert data.name.given.value == "Sri Satya Sourish"
    assert data.name.family.value == "Reddy"
    assert data.name.middle.value is None

    # 2. Address & Contact checks
    assert data.email.value == "reddysourish@gmail.com"
    assert data.phone.value == "(469)-970-9045"
    assert data.address.line1.value is None  # Never invented!
    assert data.address.line1.flag == "empty_in_resume"
    assert data.address.city.value == "Plano"
    assert data.address.state.value == "TX"
    assert data.address.postal.value == "75025"

    # 3. Links checks
    assert data.links.linkedin.value == "https://linkedin.com/in/sri-satya-sourish-reddy/"
    assert data.links.github.value == "https://github.com/Insight14"

    # 4. Education checks
    assert len(data.education) >= 1
    edu = data.education[0]
    assert "University of Texas at Dallas" in edu.school.value
    assert edu.degree.value == DegreeCanonical.BACHELORS
    assert edu.field.value == "Computer Science"
    assert edu.minor.value == "Data Science & A.I"
    assert edu.end.value == "2027-12"
    assert edu.start.value is None
    assert edu.start.flag == "empty_in_resume"

    # 5. Experience checks
    assert len(data.experience) == 4
    companies = [e.company.value for e in data.experience]
    assert "Handshake AI" in companies
    assert "The University of Texas at Dallas" in companies
    assert "iCode" in companies
    assert "Google Developer Student Club" in companies  # NOT truncated to Google!

    # Check iCode location
    icode_item = next(e for e in data.experience if e.company.value == "iCode")
    assert icode_item.location.value == "North Dallas"
    assert icode_item.title.value == "Instructor"
    assert icode_item.current.value is True

    # 6. Projects checks
    assert len(data.projects) == 4
    proj_names = [p.name.value for p in data.projects]
    assert "Uber Stall Guard" in proj_names
    assert "442ools" in proj_names

    # 7. Skills checks
    assert "Front End" in data.skills
    assert "Back End" in data.skills
    assert "React.js" in data.skills["Front End"]
    assert "Python" in data.skills["Back End"]
