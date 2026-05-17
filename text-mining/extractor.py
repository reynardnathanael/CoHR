import re
import html
import warnings
import spacy
from spacy.matcher import PhraseMatcher

try:
    from skillNer.general_params import SKILL_DB
    from skillNer.skill_extractor_class import SkillExtractor
except Exception:
    SKILL_DB = None
    SkillExtractor = None

warnings.filterwarnings("ignore", message=r"\[W008\]")

try:
    _nlp = spacy.load("en_core_web_lg")
except Exception:
    try:
        _nlp = spacy.load("en_core_web_sm")
    except Exception:
        _nlp = spacy.blank("en")
        if "sentencizer" not in _nlp.pipe_names:
            _nlp.add_pipe("sentencizer")

if SkillExtractor is not None and SKILL_DB is not None:
    _skill_extractor = SkillExtractor(_nlp, SKILL_DB, PhraseMatcher)
else:
    _skill_extractor = None

EMAIL_PATTERN = re.compile(
    r"(?<![\w.+-])([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})(?![\w.+-])"
)

PHONE_PATTERN = re.compile(
    r"""
    (?<!\d)
    (?:\+?\d{1,3}[\s.\-]?)?
    (?:\(?\d{2,4}\)?[\s.\-]?)?
    \d{3,4}[\s.\-]?\d{3,4}
    (?!\d)
    """,
    re.VERBOSE,
)

NOISY_SKILLS = {
    "a", "b", "c", "e", "m", "com", "gmail", "github", "linkedin",
    "license", "managed", "presenting", "programming", "storage",
    "teamwork", "communication", "integration", "consultant",
    "expert", "problem solve", "skills communication", "track", "rolling",
    "article", "self care", "targets", "business e", "design",
    "effectively managed", "monitored system",
}

TECH_SKILL_ALIASES = {
    "sql": ["sql", "structured query language"],
    "sql server": ["sql server", "microsoft sql server", "ms sql server", "mssql"],
    "oracle": ["oracle", "oracle database", "oracle db"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb", "mongo db"],
    "postgresql": ["postgresql", "postgres", "postgres sql"],
    "database design": ["database design", "designing database structures"],
    "database administration": ["database administration", "database admin", "dba"],
    "database architecture": ["database architecture"],
    "database engineering": ["database engineer", "database engineering"],
    "data warehousing": ["data warehousing", "data warehouse"],
    "performance tuning": ["performance tuning", "query tuning"],
    "query optimization": ["query optimization", "query optimisation"],
    "data modeling": ["data modeling", "data modelling", "data models"],
    "etl": ["etl"],
    "ssis": ["ssis"],
    "ssrs": ["ssrs"],
    ".net": [".net", "dot net"],
    "visual basic": ["visual basic", "vb"],
    "python": ["python"],
    "ruby on rails": ["ruby on rails", "rails"],
    "linux": ["linux"],
    "unix": ["unix"],
    "cloud computing": ["cloud computing"],
    "cloud migration": ["cloud migration"],
    "hybrid cloud": ["hybrid cloud"],
    "machine learning": ["machine learning"],
    "data science": ["data science"],
    "autocad": ["autocad"],
    "civil engineering": ["civil engineering"],
}

ALIAS_TO_CANONICAL = {
    alias: canonical
    for canonical, aliases in TECH_SKILL_ALIASES.items()
    for alias in aliases
}

SECTION_ALIASES = {
    "summary": [
        "summary", "profile", "professional summary", "career summary",
        "objective", "about me"
    ],
    "experience": [
        "experience", "work experience", "employment", "employment history",
        "professional experience", "work history", "career history",
        "relevant experience", "professional background",
        "research experience", "internship experience", "industry experience",
        "teaching experience", "leadership experience", "working experience",
        "experience and projects", "projects and experience"
    ],
    "education": [
        "education", "academic background", "educational background",
        "academic history", "education and training", "education training",
        "academic qualification", "academic qualifications", "qualifications",
        "academic", "academic background and education"
    ],
    "skills": [
        "skills", "technical skills", "key skills", "core skills",
        "skills summary", "competencies", "areas of expertise",
        "technical competencies", "programming skills"
    ],
    "projects": [
        "projects", "project experience", "academic projects",
        "personal projects", "selected projects", "research projects",
        "course projects", "project"
    ],
    "certifications": [
        "certifications", "certificates", "licenses", "training",
        "professional certifications"
    ],
}

INLINE_SECTION_HEADINGS = sorted(
    {
        alias
        for aliases in SECTION_ALIASES.values()
        for alias in aliases
    },
    key=len,
    reverse=True,
)


def clean_text(text):
    text = html.unescape(text or "")

    text = text.replace("<!-- image -->", " ")
    text = text.replace("¢", "-")
    text = text.replace("«", "-")
    text = text.replace("•", "\n• ")
    text = text.replace("®", "")

    # Important: do not replace or remove "@" here.
    # Removing it breaks email extraction.

    text = add_line_breaks_before_inline_sections(text)

    text = re.sub(r"^\s*#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"__", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def add_line_breaks_before_inline_sections(text):
    """
    Some PDF extractors return the whole resume as one line.
    This function puts likely section headings onto their own lines.
    """
    for heading in INLINE_SECTION_HEADINGS:
        variants = {heading.upper(), heading.title()}

        for variant in variants:
            pattern = rf"(?<!\n)(?<![A-Za-z])({re.escape(variant)})(?![A-Za-z])"
            text = re.sub(
                pattern,
                lambda match: "\n" + match.group(1) + "\n",
                text,
            )

        if len(heading.split()) > 1:
            pattern = rf"(?<!\n)(?<![A-Za-z])({re.escape(heading)})(?![A-Za-z])"
            text = re.sub(
                pattern,
                lambda match: "\n" + match.group(1) + "\n",
                text,
                flags=re.IGNORECASE,
            )

    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def normalize_line(line):
    line = line.strip().lower()
    line = re.sub(r"[:|•\-–—]+$", "", line)
    line = re.sub(r"^\W+|\W+$", "", line)
    line = re.sub(r"[^a-zA-Z&/\s]", "", line)
    line = line.replace("&", " and ")
    line = line.replace("/", " ")
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def detect_section(line):
    normalized = normalize_line(line)

    if not normalized:
        return None

    for section, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            alias = normalize_line(alias)

            if normalized == alias:
                return section

            if normalized.startswith(alias) and len(normalized.split()) <= 5:
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
    text = html.unescape(text or "")

    # Add space between camel-case words, but avoid touching emails.
    if "@" not in text:
        text = re.sub(r"(?<=\w)([A-Z][a-z]+)", r" \1", text)

    text = re.sub(r"\s+", " ", text)
    text = text.replace(" - ", " • ")
    return text.strip()


def normalize_contact_text(text):
    if not text:
        return ""

    text = html.unescape(text)

    replacements = {
        "＠": "@",
        "﹫": "@",
        "（at）": "@",
        "(at)": "@",
        "[at]": "@",
        " at ": "@",
        " dot ": ".",
        "[dot]": ".",
        "(dot)": ".",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Fix emails broken by PDF extraction, such as:
    # name @ gmail . com -> name@gmail.com
    text = re.sub(r"\s*@\s*", "@", text)
    text = re.sub(r"\s*\.\s*", ".", text)

    return text


def extract_email(text):
    if not text:
        return ""

    normalized_text = normalize_contact_text(text)

    match = EMAIL_PATTERN.search(normalized_text)
    return match.group(1) if match else ""


def extract_phone_number(text):
    if not text:
        return ""

    # Keep the original text first because some phone numbers contain spaces.
    match = PHONE_PATTERN.search(text)

    if match:
        phone = match.group(0).strip()
        phone = re.sub(r"\s+", " ", phone)
        return phone.strip("-.,;: ")

    # Fallback: handle phone numbers broken by PDF extraction.
    # This keeps digits and common phone symbols only.
    phone_like_text = re.sub(r"[^0-9+()\s.\-]", " ", text)
    phone_like_text = re.sub(r"\s+", " ", phone_like_text)

    match = PHONE_PATTERN.search(phone_like_text)

    if not match:
        return ""

    phone = match.group(0).strip()
    phone = re.sub(r"\s+", " ", phone)
    return phone.strip("-.,;: ")
def fix_missing_sections(sections, raw_text):
    """
    Fallback for resumes where the PDF parser keeps headings in strange formats.
    If experience is empty, try to recover likely experience text from raw text.
    """
    if sections.get("experience"):
        return sections

    cleaned = clean_text(raw_text)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]

    experience_keywords = [
        "experience", "work experience", "professional experience",
        "research experience", "internship experience", "employment",
        "working experience"
    ]

    stop_sections = {
        "education", "skills", "technical skills", "projects",
        "certifications", "certificates", "summary", "profile"
    }

    capturing = False
    recovered_lines = []

    for line in lines:
        normalized = normalize_line(line)

        if not capturing:
            if any(keyword in normalized for keyword in experience_keywords):
                capturing = True
            continue

        detected_section = detect_section(line)
        if detected_section and detected_section != "experience":
            break

        if normalized in stop_sections:
            break

        recovered_lines.append(line)

    if recovered_lines:
        sections["experience"] = clean_section_text(" ".join(recovered_lines))

    return sections


def extract_location(text):
    if not text:
        return ""

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    candidate_lines = []

    for line in lines[:8]:
        lowered = line.lower()

        if "@" in line or "linkedin" in lowered or "github" in lowered:
            continue

        if PHONE_PATTERN.search(line) or EMAIL_PATTERN.search(line):
            continue

        if re.search(r"\b(remote|hybrid|onsite)\b", lowered):
            candidate_lines.append(line)
            continue

        if re.search(r"^[A-Za-z .'-]+,\s*[A-Za-z .'-]{2,}$", line):
            candidate_lines.append(line)

    if candidate_lines:
        return candidate_lines[0]

    doc = _nlp("\n".join(lines[:12]))
    entities = []

    for ent in doc.ents:
        if ent.label_ in {"GPE", "LOC"}:
            value = ent.text.strip()
            if value and value not in entities:
                entities.append(value)

    if not entities:
        return ""

    if len(entities) == 1:
        return entities[0]

    return ", ".join(entities[:2])


def normalize_skill_name(skill):
    if not skill:
        return ""

    skill = html.unescape(str(skill)).lower().strip()
    skill = skill.replace("·", " ")
    skill = skill.replace("|", " ")
    skill = re.sub(r"\s+", " ", skill)
    skill = re.sub(r"^[^a-z0-9.+#]+|[^a-z0-9.+#]+$", "", skill)

    return ALIAS_TO_CANONICAL.get(skill, skill)


def is_useful_skill(skill, *, source_type=None, score=1.0):
    skill = normalize_skill_name(skill)

    if not skill or skill in NOISY_SKILLS:
        return False

    if len(skill) == 1:
        return False

    if len(skill) <= 3 and skill not in ALIAS_TO_CANONICAL.values():
        return False

    if source_type in {"oneToken", "lowSurf"} and float(score or 0) < 0.85:
        return False

    return True


def normalize_skill_search_text(text):
    text = html.unescape(text or "").lower()
    text = text.replace("/", " ")
    text = text.replace("|", " ")
    text = re.sub(r"(?<=\w)-(?=\w)", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def extract_skills_with_aliases(text):
    normalized_text = normalize_skill_search_text(text)
    found = set()

    for alias, canonical in ALIAS_TO_CANONICAL.items():
        escaped_alias = re.escape(alias).replace(r"\ ", r"\s+")
        pattern = rf"(?<![a-z0-9+#.]){escaped_alias}(?![a-z0-9+#.])"

        if re.search(pattern, normalized_text):
            found.add(canonical)

    return found


def extract_skills_with_skillner(text):
    if not text or not isinstance(text, str):
        return []

    if _skill_extractor is None:
        return sorted(extract_skills_with_aliases(text))

    annotations = _skill_extractor.annotate(text)
    skills = set()

    for item in annotations.get("results", {}).get("full_matches", []):
        skill = normalize_skill_name(item.get("doc_node_value"))

        if is_useful_skill(skill):
            skills.add(skill)

    for item in annotations.get("results", {}).get("ngram_scored", []):
        skill = normalize_skill_name(item.get("doc_node_value"))
        score = item.get("score", 0)
        source_type = item.get("type")

        if is_useful_skill(skill, source_type=source_type, score=score):
            skills.add(skill)

    skills.update(extract_skills_with_aliases(text))
    return sorted(skills)


def extract_resume_info(text):
    sections = extract_sections(text)
    sections = fix_missing_sections(sections, text)

    full_text = " ".join(sections.values())
    header_text = sections.get("header", "")

    skills_text = sections.get("skills", "")
    experience_text = sections.get("experience", "")
    projects_text = sections.get("projects", "")

    skillner_input = " ".join([
        skills_text,
        experience_text,
        projects_text,
        full_text,
    ])

    extracted_skills = extract_skills_with_skillner(skillner_input)

    # Extract contact information from the original raw text first.
    # This is safer because cleaned section text may change spacing or symbols.
    contact_text = text or ""

    combined_contact_text = "\n".join([
        contact_text,
        clean_text(contact_text),
        header_text,
        full_text,
    ])

    email = extract_email(combined_contact_text)
    phone_number = extract_phone_number(combined_contact_text)
    location = extract_location(header_text or contact_text)

    return {
        "header": sections.get("header", ""),
        "summary": sections.get("summary", ""),
        "experience": sections.get("experience", ""),
        "education": sections.get("education", ""),
        "skills_section": sections.get("skills", ""),
        "projects": sections.get("projects", ""),
        "certifications": sections.get("certifications", ""),
        "extracted_skills": extracted_skills,
        "email": email,
        "phone_number": phone_number,
        "location": location,
    }
