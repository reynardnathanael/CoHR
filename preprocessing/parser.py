"""
Parser of the input data
"""

import re
import pandas as pd

SECTION_HEADINGS = {
    "summary": [
        "summary",
        "professional summary",
    ],
    "skills": [
        "skills",
        "key skills",
        "technical skills",
    ],
    "experience": [
        "professional experience",
        "research experience",
        "work experience",
        "experience",
    ],
    "education": [
        "education",
    ],
    "achievements": [
        "achievements",
        "accomplishments",
        "honors and awards",
        "awards",
    ],
    "certifications": [
        "certifications",
        "licenses",
        "licenses and certifications",
    ],
    "publications": [
        "publications",
        "research publications",
        "selected publications",
        "papers",
    ],
    "patents": [
        "patents",
    ],
    "professional_memberships": [
        "professional memberships",
        "memberships",
        "professional affiliations",
        "affiliations",
        "professional associations",
    ],
    "references": [
        "references",
    ],
    "contact": [
        "contact information",
    ],
}


def normalize_text(text):
    text = text.replace("**", "")
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else None


def extract_phone(text):
    patterns = [
        r'\(\d{3}\)\s*\d{3}-\d{4}',
        r'\d{3}-\d{3}-\d{4}',
        r'\d{3}\s\d{3}\s\d{4}',
        r'\+?\d[\d\-\(\) ]{7,}\d'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()

    return None


def extract_linkedin(text):
    match = re.search(r'(linkedin\.com/in/[^\s\)\]]+)', text, re.IGNORECASE)
    return match.group(0) if match else None


def extract_github(text):
    match = re.search(r'(github\.com/[^\s\)\]]+)', text, re.IGNORECASE)
    return match.group(0) if match else None


def clean_line(line):
    line = line.strip()
    line = re.sub(r'^\*\s*', '', line)
    line = re.sub(r'^-\s*', '', line)
    return line.strip()


def clean_section_text(section_text):
    if not section_text:
        return ""

    lines = [clean_line(line) for line in section_text.split("\n") if line.strip()]
    return "\n".join(lines).strip()


def is_section_heading(line):
    line_clean = line.strip().lower().rstrip(":")
    for section_name, headings in SECTION_HEADINGS.items():
        if line_clean in headings:
            return section_name
    return None


def split_sections(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    sections = {"header": []}
    current_section = "header"

    for line in lines:
        found_section = is_section_heading(line)
        if found_section:
            current_section = found_section
            sections[current_section] = []
        else:
            sections.setdefault(current_section, []).append(line)

    for key in sections:
        sections[key] = "\n".join(sections[key]).strip()

    return sections


def is_intro_line(line):
    line_clean = line.strip().lower()

    intro_patterns = [
        r"^here'?s\s+a\s+.*resume\s+for\s+.*:?\s*$",
        r"^here\s+is\s+a\s+.*resume\s+for\s+.*:?\s*$",
        r"^this\s+is\s+a\s+.*resume\s+for\s+.*:?\s*$",
    ]

    for pattern in intro_patterns:
        if re.match(pattern, line_clean):
            return True

    return False


def looks_like_name(line):
    if not line:
        return False

    line = line.strip()

    if len(line.split()) < 2 or len(line.split()) > 4:
        return False

    if is_section_heading(line):
        return False

    lower_line = line.lower()
    bad_keywords = [
        "email", "phone", "linkedin", "github", "summary", "skills",
        "experience", "education", "certifications", "references",
        "resume", "professional", "sample", "contact"
    ]
    if any(word in lower_line for word in bad_keywords):
        return False

    if re.search(r'[@:/\d\(\)\[\]]', line):
        return False

    if not re.match(r"^[A-Za-z][A-Za-z\s\.\-']+$", line):
        return False

    return True


def looks_like_title(line):
    if not line:
        return False

    line = line.strip()

    if is_section_heading(line):
        return False

    lower_line = line.lower()
    bad_keywords = [
        "email", "phone", "linkedin", "github", "contact information"
    ]
    if any(word in lower_line for word in bad_keywords):
        return False

    if re.search(r'[@:/\[\]]', line):
        return False

    if len(line.split()) > 8:
        return False

    return True


def extract_name_and_title(header_text):
    lines = [line.strip() for line in header_text.split("\n") if line.strip()]

    cleaned_lines = []
    for line in lines:
        lower_line = line.lower().strip()

        if is_intro_line(line):
            continue
        if lower_line.startswith("note:"):
            continue
        if is_section_heading(line):
            continue

        cleaned_lines.append(line)

    name = None
    title = None

    for i, line in enumerate(cleaned_lines):
        if looks_like_name(line):
            name = line
            if i + 1 < len(cleaned_lines) and looks_like_title(cleaned_lines[i + 1]):
                title = cleaned_lines[i + 1]
            break

    if name is None and len(cleaned_lines) > 0:
        name = cleaned_lines[0]

    if title is None and len(cleaned_lines) > 1:
        if cleaned_lines[1] != name and looks_like_title(cleaned_lines[1]):
            title = cleaned_lines[1]

    return name, title


def extract_summary(sections):
    return clean_section_text(sections.get("summary", ""))


def split_colon_skill_groups(line):
    """
    Handle lines like:
    Programming Languages: Python, R, SQL, Machine Learning: Scikit-learn, TensorFlow, PyTorch

    Output:
    ['Python', 'R', 'SQL', 'Scikit-learn', 'TensorFlow', 'PyTorch']
    """
    pattern = r'([^:]+):'
    matches = list(re.finditer(pattern, line))

    if not matches:
        return []

    items = []

    for i, match in enumerate(matches):
        start_content = match.end()
        end_content = matches[i + 1].start() if i + 1 < len(matches) else len(line)

        content = line[start_content:end_content].strip()
        content = content.strip(", ").strip()

        if content:
            parts = [part.strip() for part in content.split(",") if part.strip()]
            items.extend(parts)

    return items


def extract_skills(skills_text):
    """
    Unified skill parser for both:
    1. Non-engineer style:
       Inventory management software (TradeGecko, Zoho Inventory)
    2. Engineer style:
       Programming Languages: Python, R, SQL
    3. Mixed multiple groups in one line:
       Programming Languages: Python, R, SQL, Machine Learning: Scikit-learn, TensorFlow
    """
    if not skills_text:
        return ""

    lines = [clean_line(line) for line in skills_text.split("\n") if line.strip()]
    all_skills = []

    for line in lines:
        line = line.strip().rstrip(".").strip()

        if not line:
            continue

        # Case 1: multiple colon groups in one line
        colon_group_items = split_colon_skill_groups(line)
        if colon_group_items:
            for item in colon_group_items:
                item_clean = re.sub(r'(?i)\betc\.?$', '', item).strip()
                item_clean = item_clean.strip(", ").strip()
                if item_clean:
                    all_skills.append(item_clean)
            continue

        # Case 2: parentheses style
        match = re.match(r'^(.*?)\s*\((.*?)\)\s*$', line)
        if match:
            main_skill = match.group(1).strip()
            inside_text = match.group(2).strip()

            if main_skill:
                main_skill = re.sub(r'(?i)\betc\.?$', '', main_skill).strip(", ").strip()
                if main_skill:
                    all_skills.append(main_skill)

            inside_items = [item.strip() for item in inside_text.split(",") if item.strip()]
            for item in inside_items:
                item_clean = re.sub(r'(?i)\betc\.?$', '', item).strip()
                item_clean = item_clean.strip(", ").strip()
                if item_clean:
                    all_skills.append(item_clean)
            continue

        # Case 3: plain skill line
        line_clean = re.sub(r'(?i)\betc\.?$', '', line).strip()
        line_clean = line_clean.strip(", ").strip()
        if line_clean:
            all_skills.append(line_clean)

    seen = set()
    unique_skills = []
    for skill in all_skills:
        skill_key = skill.lower()
        if skill_key not in seen:
            seen.add(skill_key)
            unique_skills.append(skill)

    return ", ".join(unique_skills)


def extract_experience(sections):
    return clean_section_text(sections.get("experience", ""))


def extract_education(sections):
    return clean_section_text(sections.get("education", ""))


def extract_certifications(sections):
    return clean_section_text(sections.get("certifications", ""))


def extract_achievements(sections):
    return clean_section_text(sections.get("achievements", ""))


def extract_publications(sections):
    return clean_section_text(sections.get("publications", ""))


def extract_patents(sections):
    return clean_section_text(sections.get("patents", ""))


def extract_professional_memberships(sections):
    return clean_section_text(sections.get("professional_memberships", ""))


def extract_references(sections):
    return clean_section_text(sections.get("references", ""))


def parse_resume(text, resume_id=None):
    text = normalize_text(text)
    sections = split_sections(text)

    name, title = extract_name_and_title(sections.get("header", ""))

    data = {
        "resume_id": resume_id,
        "name": name,
        "title": title,
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_linkedin(text),
        "github": extract_github(text),
        "summary": extract_summary(sections),
        "skills": extract_skills(sections.get("skills", "")),
        "experience": extract_experience(sections),
        "education": extract_education(sections),
        "certifications": extract_certifications(sections),
        "achievements": extract_achievements(sections),
        "publications": extract_publications(sections),
        "patents": extract_patents(sections),
        "professional_memberships": extract_professional_memberships(sections),
        "references": extract_references(sections),
        "raw_text": text,
    }

    return data