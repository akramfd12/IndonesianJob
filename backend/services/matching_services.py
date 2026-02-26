# =========================================================
# CV MATCHING SERVICE
# =========================================================
# This module handles:
# - PDF text extraction
# - CV structuring using LLM
# - Building semantic query for vector search
# =========================================================

from pypdf import PdfReader
import json
from config import client
from db.qdrant import get_vector_store
from agents.tools import *


# =========================================================
# 1️⃣ Extract Text from Uploaded PDF
# =========================================================
# Reads PDF file and extracts raw text content
# from all pages.
def extract_text_from_upload(file) -> str:
    reader = PdfReader(file.file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


# =========================================================
# 2️⃣ Build Prompt for CV Structuring
# =========================================================
# Creates a strict JSON-format instruction prompt
# to transform raw CV text into structured data.
def build_cv_structuring_prompt(cv_text: str) -> str:
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


# =========================================================
# 3️⃣ Parse CV Using LLM
# =========================================================
# Sends CV text to OpenAI model to:
# - Convert raw text into structured JSON format
# - Enforce strict JSON output
def parse_cv_with_llm(cv_text: str) -> dict:

    # Build structured prompt
    prompt = build_cv_structuring_prompt(cv_text)

    # Call OpenAI Chat Completion API
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a strict JSON generator."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract model output
    content = response.choices[0].message.content

    # Validate JSON response
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON")


# =========================================================
# 4️⃣ Build Semantic Query from Structured CV
# =========================================================
# Converts structured CV JSON into a natural-language
# query used for vector similarity search.
def build_cv_query(structured_cv: dict) -> str:

    # Combine work experience entries
    experience_text = "\n".join([
        f"{exp.get('title', '')} at {exp.get('company', '')} "
        f"({exp.get('duration', '')}): {exp.get('description', '')}"
        for exp in structured_cv.get("experience", [])
    ]) or "Not provided"

    # Combine project descriptions
    project_text = "\n".join([
        f"{proj.get('name', '')}: {proj.get('description', '')}"
        for proj in structured_cv.get("projects", [])
    ]) or "Not provided"

    # Education summary
    education_text = structured_cv.get("education", "") or "Not provided"

    # Technical skills list
    skills_text = ", ".join(
        structured_cv.get("technical_skills", [])
    ) or "Not provided"

    # Software skills list
    software_text = ", ".join(
        structured_cv.get("software_skills", [])
    ) or "Not provided"

    # Build final semantic query text
    return (
        f"Education:\n{education_text}\n\n"
        f"Experience:\n{experience_text}\n\n"
        f"Projects:\n{project_text}\n\n"
        f"Technical Skills:\n{skills_text}\n\n"
        f"Software Skills:\n{software_text}"
    )