from pypdf import PdfReader
from rapidfuzz import fuzz
import re

def extract_text_from_pdf(file_path: str):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

extract_cv = extract_text_from_pdf(file_path=r"E:\PortoProject\IndonesianJob\CV_Muhammad Fakhrul Ikram_260203.pdf")

SECTION_SYNONYMS = {

    "summary": [
        # English
        "career objective",
        "objective",
        "summary",
        "professional summary",
        "profile",
        "about me",

        # Indonesia
        "ringkasan",
        "ringkasan profil",
        "tujuan karir",
        "profil",
        "tentang saya",
        "deskripsi diri"
    ],

    "education": [
        # English
        "education",
        "academic background",
        "educational history",
        "qualification",

        # Indonesia
        "pendidikan",
        "riwayat pendidikan",
        "latar belakang pendidikan",
        "kualifikasi pendidikan"
    ],

    "experience": [
        # English
        "work experience",
        "professional experience",
        "employment",
        "career history",
        "work history",

        # Indonesia
        "pengalaman kerja",
        "pengalaman profesional",
        "riwayat pekerjaan",
        "riwayat kerja",
        "karir"
    ],

    "projects": [
        # English
        "project",
        "projects",
        "personal project",
        "portfolio",
        "case study",
        "research project",

        # Indonesia
        "proyek",
        "projek",
        "portfolio proyek",
        "studi kasus",
        "pengalaman proyek"
    ],

    "technical_skills": [
        # English
        "technical skills",
        "technical expertise",
        "core skills",
        "hard skills",

        # Indonesia
        "keahlian teknis",
        "kemampuan teknis",
        "keterampilan teknis",
        "hard skill"
    ],

    "software_skills": [
        # English
        "software skills",
        "tools",
        "technologies",
        "tech stack",

        # Indonesia
        "perangkat lunak",
        "tools dan teknologi",
        "teknologi",
        "stack teknologi"
    ],

    "soft_skills": [
        # English
        "soft skills",
        "personal skills",
        "interpersonal skills",

        # Indonesia
        "soft skill",
        "kemampuan pribadi",
        "keterampilan pribadi",
        "kemampuan interpersonal"
    ]
}

def normalize(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return text.strip()

def detect_section(header):
    header_norm = normalize(header)

    best_match = None
    best_score = 0

    for section, keywords in SECTION_SYNONYMS.items():
        for keyword in keywords:
            score = fuzz.token_sort_ratio(header_norm, keyword)

            if score > best_score:
                best_score = score
                best_match = section

    if best_score >= 85:
        return best_match
    
    return None

def split_cv_into_sections(cv_text):
    lines = cv_text.split("\n")

    sections = {}
    current_section = None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        detected = None

        if len(line.split()) <= 6:
            detected = detect_section(line)

        if detected:
            current_section = detected
            sections[current_section] = []
            continue

        if current_section:
            sections[current_section].append(line)

    for sec in sections:
        sections[sec] = "\n".join(sections[sec]).strip()

    return sections

def build_cv_query(structured_cv: dict):
    structured_cv = split_cv_into_sections(extract_cv)
    return f"""
    Experience:
    {structured_cv.get("experience", "")}

    Education:
    {structured_cv.get("education", "")}

    Technical Skills:
    {structured_cv.get("technical_skills", "")}

    Software Skills:
    {structured_cv.get("software_skills", "")}
    """