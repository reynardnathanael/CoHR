import re
import html
from skill_extractor import extract_skills_with_skillner


SECTION_ALIASES = {
    "summary": [
        "summary", "profile", "professional summary", "career summary",
        "objective", "about me"
    ],
    "experience": [
        "experience", "work experience", "employment", "employment history",
        "professional experience", "work history", "career history"
    ],
    "education": [
        "education", "academic background", "educational background",
        "academic history"
    ],
    "skills": [
        "skills", "technical skills", "key skills", "core skills",
        "skills summary", "competencies", "areas of expertise"
    ],
    "projects": [
        "projects", "project experience", "academic projects",
        "personal projects"
    ],
    "certifications": [
        "certifications", "certificates", "licenses", "training"
    ],
}


def clean_text(text):
    text = html.unescape(text)

    text = text.replace("<!-- image -->", " ")
    text = text.replace("¢", "-")
    text = text.replace("«", "-")
    text = text.replace("®", "")
    text = text.replace("@", " ")

    text = re.sub(r"^\s*#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def normalize_line(line):
    line = line.strip().lower()
    line = re.sub(r"^\W+|\W+$", "", line)
    line = re.sub(r"[^a-zA-Z\s]", "", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def detect_section(line):
    normalized = normalize_line(line)

    for section, aliases in SECTION_ALIASES.items():
        if normalized in aliases:
            return section

    return None


def extract_sections(text):
    text = clean_text(text)
    lines = text.splitlines()

    sections = {"header": []}
    current_section = "header"

    for line in lines:
        line = line.strip()

        if not line:
            continue

        detected_section = detect_section(line)

        if detected_section:
            current_section = detected_section
            sections.setdefault(current_section, [])
            continue

        sections.setdefault(current_section, []).append(line)

    return {
        section: clean_section_text(" ".join(content))
        for section, content in sections.items()
    }


def clean_section_text(text):
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    text = text.replace(" - ", " • ")
    return text.strip()


def fallback_extract_education(text):
    degree_patterns = [
        r"(bachelor[^.|\n]*)",
        r"(master[^.|\n]*)",
        r"(ph\.?d[^.|\n]*)",
        r"(b\.s\.[^.|\n]*)",
        r"(m\.s\.[^.|\n]*)",
        r"(computer science[^.|\n]*)",
        r"(data science[^.|\n]*)",
    ]

    matches = []

    for pattern in degree_patterns:
        found = re.findall(pattern, text, flags=re.IGNORECASE)
        matches.extend(found)

    return " ".join(matches[:3]).strip()


def fallback_extract_experience(text):
    experience_keywords = [
        "engineer", "developer", "scientist", "analyst",
        "manager", "consultant", "intern"
    ]

    lines = clean_text(text).splitlines()
    selected = []

    for line in lines:
        line_lower = line.lower()

        if any(keyword in line_lower for keyword in experience_keywords):
            selected.append(line.strip())

    return " ".join(selected[:10]).strip()


def parse_resume_info(file_name, raw_text):
    cleaned = clean_text(raw_text)
    sections = extract_sections(cleaned)

    education = sections.get("education", "")
    experience = sections.get("experience", "")
    skills_section = sections.get("skills", "")

    if len(education) < 20:
        education = fallback_extract_education(cleaned)

    if len(experience) < 20:
        experience = fallback_extract_experience(cleaned)

    # Prefer skills section for precision; fallback to full text for recall.
    if len(skills_section) >= 20:
        skills = extract_skills_with_skillner(
            skills_section,
            include_ngram=True,
            ngram_min_score=0.80,
        )

        if len(skills) < 5:
            extra_skills = extract_skills_with_skillner(cleaned, include_ngram=False)
            for skill in extra_skills:
                if skill not in skills:
                    skills.append(skill)
    else:
        skills = extract_skills_with_skillner(
            cleaned,
            include_ngram=True,
            ngram_min_score=0.80,
        )

    skills = sorted(skills)

    return {
        "file_name": file_name,
        "full_text": cleaned,
        "summary": sections.get("summary", ""),
        "experience": experience,
        "education": education,
        "skills_section": skills_section,
        "projects": sections.get("projects", ""),
        "certifications": sections.get("certifications", ""),
        "extracted_skills": skills,
    }