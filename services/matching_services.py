from pypdf import PdfReader
import json
from config import client
from db.qdrant import get_vector_store
from agents.tools import *

def extract_text_from_pdf(file_path: str):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

# cv_text = extract_text_from_pdf(file_path=r"E:\PortoProject\IndonesianJob\CV_Muhammad Fakhrul Ikram_260203.pdf")

def build_cv_structuring_prompt():
    cv_text = extract_text_from_pdf(file_path=r"E:\PortoProject\IndonesianJob\CV_Muhammad Fakhrul Ikram_260203.pdf")
    return f"""
    You are a professional CV parser.

    Extract structured information from the CV below.

    Return ONLY valid JSON.
    Do not explain anything.
    Do not add extra text.

    If a section does not exist, return empty string "" or empty list [].

    JSON format:
    
    {{
    "summary": "",
    "education": "",
    "experience": [
        {{
        "title": "",
        "company": "",
        "duration": "",
        "description": ""
        }}
    ],
    "projects": [
        {{
        "name": "",
        "description": ""
        }}
    ],
    "technical_skills": [],
    "software_skills": [],
    "soft_skills": []
    }}

    CV TEXT:
    {cv_text}
    """

def parse_cv_with_llm(prompt: str):

    prompt = build_cv_structuring_prompt()
    
    response = client.chat.completions.create(
        model="gpt-5-mini",   # bisa pakai model lain juga
        messages=[
            {"role": "system", "content": "You are a strict JSON generator."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON")

def build_cv_query(structured_cv: dict):
    experience_text = "\n".join([
        f"{exp['title']} at {exp['company']} ({exp['duration']}): {exp['description']}"
        for exp in structured_cv.get("experience", [])
    ])

    project_text = "\n".join([
        f"{proj['name']}: {proj['description']}"
        for proj in structured_cv.get("projects", [])
    ])

    skills_text = ", ".join(structured_cv.get("technical_skills", []))
    software_text = ", ".join(structured_cv.get("software_skills", []))

    return (
        f"Experience:\n{experience_text}\n\n"
        f"Projects:\n{project_text}\n\n"
        f"Technical Skills:\n{skills_text}\n\n"
        f"Software Skills:\n{software_text}"
    )


# def cv_search_jobs(query_text:str, k: int = 5) -> list:

#     vectorstore = get_vector_store("indonesianjobs_collection")

#     results = vectorstore.similarity_search_with_score(
#         query_text,
#         k=5
#     )

#     return results
# query_text = build_cv_query(structured_cv = parse_cv_with_llm(cv_text))

# test = cv_search_jobs(query_text)

# print(test)