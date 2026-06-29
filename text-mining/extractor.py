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


LOCATION_BAD_KEYWORDS = {
    "curriculum vitae", "resume", "cv", "personal", "information",
    "personal information", "contact", "contact information",
    "summary", "profile", "skills", "education", "experience",
    "projects", "certifications", "certificates", "github",
    "linkedin", "portfolio"
}

LOCATION_SIGNAL_WORDS = {
    "remote", "hybrid", "onsite", "on-site"
}


def add_line_breaks_before_inline_sections(text):
    for heading in INLINE_SECTION_HEADINGS:
        variants = {heading.upper(), heading.title()}

        for variant in variants:
            pattern = rf"(?<!\n)(?<![A-Za-z])({re.escape(variant)})(?![A-Za-z])"
            text = re.sub(pattern, lambda m: "\n" + m.group(1) + "\n", text)

        if len(heading.split()) > 1:
            pattern = rf"(?<!\n)(?<![A-Za-z])({re.escape(heading)})(?![A-Za-z])"
            text = re.sub(
                pattern,
                lambda m: "\n" + m.group(1) + "\n",
                text,
                flags=re.IGNORECASE,
            )

    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def clean_text(text):
    text = html.unescape(text or "")

    text = text.replace("<!-- image -->", " ")
    text = text.replace("¢", "-")
    text = text.replace("«", "-")
    text = text.replace("•", "\n• ")
    text = text.replace("®", "")

    text = add_line_breaks_before_inline_sections(text)

    text = re.sub(r"^\s*#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"__", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


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


def clean_section_text(text):
    text = html.unescape(text or "")

    if "@" not in text:
        text = re.sub(r"(?<=\w)([A-Z][a-z]+)", r" \1", text)

    # Preserve newlines but squash horizontal spaces so we can split by line later
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = text.replace(" - ", " • ")
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


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
        section: clean_section_text("\n".join(content))
        for section, content in sections.items()
    }


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

    match = PHONE_PATTERN.search(text)

    if match:
        phone = match.group(0).strip()
        phone = re.sub(r"\s+", " ", phone)
        return phone.strip("-.,;: ")

    phone_like_text = re.sub(r"[^0-9+()\s.\-]", " ", text)
    phone_like_text = re.sub(r"\s+", " ", phone_like_text)

    match = PHONE_PATTERN.search(phone_like_text)

    if not match:
        return ""

    phone = match.group(0).strip()
    phone = re.sub(r"\s+", " ", phone)

    return phone.strip("-.,;: ")


def fix_missing_sections(sections, raw_text):
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
        sections["experience"] = clean_section_text("\n".join(recovered_lines))

    return sections


def clean_location_candidate(line):
    line = html.unescape(line or "").strip()

    # Remove OCR/icon noise at the beginning of the line.
    line = re.sub(r"^[^\w@+]*[📍½⌂🏠🌐]?\s*", "", line)

    line = re.sub(r"\s+", " ", line)
    line = line.strip(" |•-–—,:;")

    return line


def is_bad_location_candidate(line):
    lowered = line.lower().strip()

    if not line or len(line) < 3:
        return True

    if any(keyword in lowered for keyword in LOCATION_BAD_KEYWORDS):
        return True

    if "@" in line:
        return True

    if EMAIL_PATTERN.search(line):
        return True

    if PHONE_PATTERN.search(line):
        return True

    if "http" in lowered or "www." in lowered:
        return True

    if len(line.split()) > 6:
        return True

    return False


def looks_like_location_format(line):
    lowered = line.lower().strip()

    if lowered in LOCATION_SIGNAL_WORDS:
        return True

    # City, Country / City, State
    if re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ .'-]+,\s*[A-Za-zÀ-ÖØ-öø-ÿ .'-]+$", line):
        return True

    # City | Country or City - Country
    if re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ .'-]+\s*[\|/–-]\s*[A-Za-zÀ-ÖØ-öø-ÿ .'-]+$", line):
        return True

    return False


def extract_location(text):
    if not text:
        return ""

    cleaned_text = clean_text(text)
    lines = [line.strip() for line in cleaned_text.splitlines() if line.strip()]

    header_text = "\n".join(lines[:30])
    doc = _nlp(header_text)

    candidates = []

    # 1. NER-first approach
    for ent in doc.ents:
        if ent.label_ in {"GPE", "LOC"}:
            candidate = clean_location_candidate(ent.text)

            if is_bad_location_candidate(candidate):
                continue

            if candidate not in candidates:
                candidates.append(candidate)

    if candidates:
        return candidates[0]

    # 2. Fallback for common resume location formats
    for line in lines[:25]:
        candidate = clean_location_candidate(line)

        if is_bad_location_candidate(candidate):
            continue

        if looks_like_location_format(candidate):
            return candidate

    return ""


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


def extract_name(text):
    if not text:
        return ""

    cleaned_text = clean_text(text)
    lines = [line.strip() for line in cleaned_text.splitlines() if line.strip()]
    if not lines:
        return ""
        
    invalid_names = sorted({
        "resume", "curriculum vitae", "cv", "profile", "summary", 
        "personal information", "contact", "contact info", "contact information",
        "experience", "education", "skills", "projects", "certifications", 
        "languages", "portfolio", "github", "linkedin", "address", "phone", "email",
        "website", "http", "https", "www", "page", "info", "information"
    }, key=len, reverse=True)

    def clean_name_line(line):
        # Strip common resume noise like emails, phones, and urls
        line = re.sub(r"[\w\.-]+@[\w\.-]+", "", line)
        line = re.sub(r"\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", "", line)
        line = re.sub(r"https?://\S+", "", line, flags=re.IGNORECASE)
        line = re.sub(r"www\.\S+", "", line, flags=re.IGNORECASE)
        line = re.sub(r"(github|linkedin)\.com/\S+", "", line, flags=re.IGNORECASE)
        
        # Pre-emptively remove invalid words so they don't count towards the word limit
        for invalid in invalid_names:
            line = re.sub(rf"\b{re.escape(invalid)}\b", "", line, flags=re.IGNORECASE)
            
        clean = re.sub(r"[^a-zA-Z\s\-']", " ", line).strip()
        return re.sub(r"\s+", " ", clean).strip()

    # 1. Try NER on the first 15 lines
    header = "\n".join(lines[:15])
    if header.isupper():
        header = header.title()
    doc = _nlp(header)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = clean_name_line(ent.text)
            if 0 < len(name.split()) <= 4:
                return name.title()

    # 2. Fallback: check the first 5 lines for a short 1-4 word line
    for line in lines[:5]:
        clean_line = clean_name_line(line)
        if not clean_line:
            continue
        words = clean_line.split()
        if 0 < len(words) <= 4:
            return clean_line.title()

    # 3. Fallback: If the first few lines are flattened strings, split by common separators
    for line in lines[:3]:
        for invalid in invalid_names:
            line = re.sub(rf"\b{re.escape(invalid)}\b", "|", line, flags=re.IGNORECASE)
        parts = re.split(r"[|•\-–—:;,]", line)
        if len(parts) > 1:
            for part in parts:
                clean_part = clean_name_line(part)
                if not clean_part:
                    continue
                words = clean_part.split()
                if 0 < len(words) <= 4:
                    return clean_part.title()

    # 4. Ultimate Fallback: Aggressively grab the first 2 words from the cleaned text
    for line in lines[:3]:
        clean_line = clean_name_line(line)
        if not clean_line:
            continue
        words = clean_line.split()
        if len(words) >= 2:
            return " ".join(words[:2]).title()
        elif len(words) == 1:
            return words[0].title()

    return ""


BACHELOR_PATTERN = re.compile(r"\b(bachelor|bachelors|bsc|b\.sc|b\.a|b\.s|b\.e|b\.tech|bs|ba|undergraduate|bba|bfa)\b", re.IGNORECASE)
MASTER_PATTERN = re.compile(r"\b(master|masters|msc|m\.sc|m\.a|m\.s|m\.e|m\.tech|ms|ma|mba|postgraduate)\b", re.IGNORECASE)
PHD_PATTERN = re.compile(r"\b(phd|ph\.d|doctorate|doctoral|md|j\.d|jd)\b", re.IGNORECASE)

DATE_RANGE_PATTERN = re.compile(
    r"(?P<start>"
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
    r"Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[.\s-]*\d{4}"
    r"|\d{4}"
    r")\s*(?:-|–|—|to|through|until|until\s+)?\s*"
    r"(?P<end>"
    r"(?:present|current|now|Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
    r"Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[.\s-]*\d{4}?"
    r"|\d{4}"
    r")",
    re.IGNORECASE,
)

SINGLE_DATE_PATTERN = re.compile(
    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
    r"Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[.\s-]*\d{4}\b|\b\d{4}\b",
    re.IGNORECASE,
)


def _split_candidate_blocks(text):
    if not text:
        return []

    cleaned = clean_section_text(text)
    blocks = []
    current = []

    for line in cleaned.splitlines():
        line = line.strip()
        if not line:
            if current:
                blocks.append("\n".join(current).strip())
                current = []
            continue

        current.append(line.lstrip("•-*— ").strip())

    if current:
        blocks.append("\n".join(current).strip())

    return [block for block in blocks if block]


def _extract_date_range(text):
    if not text:
        return "", ""

    match = DATE_RANGE_PATTERN.search(text)
    if match:
        start = re.sub(r"\s+", " ", match.group("start") or "").strip(" ,;:-")
        end = re.sub(r"\s+", " ", match.group("end") or "").strip(" ,;:-")
        return start, end

    dates = SINGLE_DATE_PATTERN.findall(text)
    dates = [re.sub(r"\s+", " ", date).strip(" ,;:-") for date in dates if date]
    if len(dates) >= 2:
        return dates[0], dates[1]
    if len(dates) == 1:
        return dates[0], ""

    return "", ""


def _is_date_like(text):
    if not text:
        return False
    return bool(DATE_RANGE_PATTERN.search(text) or SINGLE_DATE_PATTERN.search(text))


def _extract_org_candidates(text):
    if not text:
        return []

    candidates = []
    keyword_lines = []
    org_keywords = (
        "university", "college", "institute", "school", "academy", "company",
        "corp", "corporation", "inc", "ltd", "llc", "laboratory", "lab",
        "center", "centre", "association", "foundation"
    )

    for line in text.splitlines():
        lowered = line.lower()
        if any(keyword in lowered for keyword in org_keywords):
            cleaned = re.sub(r"\s+", " ", line).strip(" ,;:-")
            if cleaned and cleaned not in keyword_lines:
                keyword_lines.append(cleaned)

    doc = _nlp(text)
    for ent in doc.ents:
        if ent.label_ == "ORG":
            value = re.sub(r"\s+", " ", ent.text).strip(" ,;:-")
            if value and value not in candidates:
                candidates.append(value)
    for item in keyword_lines:
        if item not in candidates:
            candidates.append(item)
    return candidates


def _extract_urls(text):
    if not text:
        return []
    urls = []
    for match in re.findall(r"https?://\S+|www\.\S+", text, flags=re.IGNORECASE):
        cleaned = match.strip(").,;]")
        if cleaned and cleaned not in urls:
            urls.append(cleaned)
    return urls


def _extract_degree_text(part):
    lines = [line.strip() for line in part.splitlines() if line.strip()]
    for line in lines:
        if BACHELOR_PATTERN.search(line) or MASTER_PATTERN.search(line) or PHD_PATTERN.search(line):
            return re.sub(r"\s+", " ", line).strip()
    return ""


def _extract_major_text(part):
    major_match = re.search(r"(?:major|speciali[sz]ation|field of study|concentration)\s*[:\-]?\s*([^,\n]+)", part, re.IGNORECASE)
    if major_match:
        return re.sub(r"\s+", " ", major_match.group(1)).strip(" ,;:-")
    return ""


def _extract_location_text(part):
    location = extract_location(part)
    if location:
        return location
    return ""


def _infer_education_bucket(part):
    if PHD_PATTERN.search(part):
        return "phd_edu"
    if MASTER_PATTERN.search(part):
        return "master_edu"
    if BACHELOR_PATTERN.search(part):
        return "bachelor_edu"
    return "other_edu"


def _education_bucket_field(bucket):
    if bucket == "bachelor_edu":
        return "bachelor_university", "bachelor_degree", "bachelor_major"
    if bucket == "master_edu":
        return "master_university", "master_degree", "master_major"
    if bucket == "phd_edu":
        return "phd_university", "phd_degree", "phd_major"
    return "other_university", "other_degree", "other_major"


def _education_entry_template(bucket):
    university_key, degree_key, major_key = _education_bucket_field(bucket)
    return {
        university_key: "",
        degree_key: "",
        major_key: "",
        "start_date": "",
        "end_date": "",
        "details": [],
        "raw_text": "",
    }


def _education_entry_is_empty(entry):
    return not any(
        value
        for key, value in entry.items()
        if key != "details" and key != "raw_text" and isinstance(value, str) and value.strip()
    ) and not entry.get("details")


def parse_education_detailed(text):
    education = {
        "bachelor_edu": [],
        "master_edu": [],
        "phd_edu": [],
        "other_edu": [],
    }

    if not text:
        return education

    lines = [line.strip(" •-—\t") for line in clean_section_text(text).splitlines() if line.strip()]
    current_bucket = None
    current_entry = None
    pending_university = ""
    pending_dates = []

    def finalize_entry():
        nonlocal current_bucket, current_entry
        if not current_entry:
            return
        if _education_entry_is_empty(current_entry):
            current_bucket = None
            current_entry = None
            return
        university_key, degree_key, major_key = _education_bucket_field(current_bucket)
        clean_entry = {
            university_key: current_entry.get(university_key, ""),
            degree_key: current_entry.get(degree_key, ""),
            major_key: current_entry.get(major_key, ""),
            "start_date": current_entry.get("start_date", ""),
            "end_date": current_entry.get("end_date", ""),
            "details": current_entry.get("details", []),
            "raw_text": "\n".join(
                part for part in [
                    current_entry.get(university_key, ""),
                    " ".join(
                        item for item in [
                            current_entry.get("start_date", ""),
                            current_entry.get("end_date", ""),
                        ]
                        if item
                    ),
                    current_entry.get(degree_key, ""),
                    current_entry.get(major_key, ""),
                    *current_entry.get("details", []),
                ]
                if part
            ),
        }
        if current_bucket:
            education[current_bucket].append(clean_entry)
        current_bucket = None
        current_entry = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        is_degree = bool(BACHELOR_PATTERN.search(line) or MASTER_PATTERN.search(line) or PHD_PATTERN.search(line))
        is_date = _is_date_like(line)
        org_candidates = _extract_org_candidates(line)
        is_org = bool(org_candidates)

        if is_degree:
            if current_entry and current_entry.get("degree") and current_entry.get("degree") != line:
                finalize_entry()
            if current_entry is None:
                current_bucket = _infer_education_bucket(line)
                current_entry = _education_entry_template(current_bucket)
            university_key, degree_key, major_key = _education_bucket_field(current_bucket)
            current_entry[degree_key] = line
            current_entry["degree"] = line
            major_text = _extract_major_text(line)
            if major_text:
                current_entry[major_key] = major_text
                current_entry["major"] = major_text
            if pending_university and not current_entry[university_key]:
                current_entry[university_key] = pending_university
            if pending_dates and not current_entry.get("start_date"):
                date_text = " ".join(pending_dates)
                start_date, end_date = _extract_date_range(date_text)
                current_entry["start_date"] = start_date
                current_entry["end_date"] = end_date
            pending_university = ""
            pending_dates = []
            continue

        if is_date:
            if current_entry is not None:
                university_key, _, _ = _education_bucket_field(current_bucket)
                if not current_entry.get("start_date") and not current_entry.get("end_date"):
                    start_date, end_date = _extract_date_range(line)
                    current_entry["start_date"] = start_date
                    current_entry["end_date"] = end_date
                elif current_entry.get(university_key) and current_entry.get("degree"):
                    finalize_entry()
                    pending_dates.append(line)
                elif line not in current_entry.get("details", []):
                    current_entry["details"].append(line)
            else:
                pending_dates.append(line)
            continue

        if is_org:
            if current_entry is None:
                pending_university = org_candidates[0]
                continue

            university_key, _, _ = _education_bucket_field(current_bucket)
            if not current_entry.get(university_key):
                current_entry[university_key] = org_candidates[0]
            elif current_entry.get(university_key) and current_entry.get("start_date") and current_entry.get("degree"):
                finalize_entry()
                pending_university = org_candidates[0]
            elif line not in current_entry.get("details", []):
                current_entry["details"].append(line)
            continue

        if current_entry is None:
            continue

        if current_entry.get("degree") and line not in current_entry.get("details", []):
            current_entry["details"].append(line)

    finalize_entry()

    # If we saw preamble lines before the first degree and never attached them,
    # keep only genuinely uncategorized leftovers in other_edu.
    if pending_university and not any(education.values()):
        education["other_edu"].append({"other_text": pending_university, "raw_text": pending_university, "details": []})
    if pending_dates and not any(education.values()):
        date_text = " ".join(pending_dates).strip()
        if date_text:
            education["other_edu"].append({"other_text": date_text, "raw_text": date_text, "details": []})

    return education


def parse_experience_detailed(text):
    experience = []
    if not text:
        return experience

    for part in _split_candidate_blocks(text):
        lines = [line.strip(" •-—") for line in part.splitlines() if line.strip()]
        if not lines:
            continue

        start_date, end_date = _extract_date_range(part)
        experience_date = " - ".join([item for item in [start_date, end_date] if item])
        title = ""
        company = ""

        first_line = lines[0]
        if "," in first_line:
            title_candidate, company_candidate = [piece.strip() for piece in first_line.split(",", 1)]
            title = title_candidate
            company = company_candidate
        else:
            title = first_line

        org_candidates = _extract_org_candidates(part)
        if org_candidates:
            company = company or org_candidates[0]

        location = _extract_location_text(part)
        description_lines = [
            line for line in lines[1:]
            if line not in {company, location, start_date, end_date}
            and not _is_date_like(line)
        ]
        description = " ".join(description_lines).strip()
        if not description and len(lines) > 1:
            description = " ".join(lines[1:]).strip()

        experience.append(
            {
                "experience_title": title,
                "experience_description": description,
                "experience_date": experience_date,
                "company": company,
                "location": location,
                "raw_text": part,
            }
        )

    return experience


def parse_project_detailed(text):
    projects = []
    if not text:
        return projects

    for part in _split_candidate_blocks(text):
        lines = [line.strip(" •-—") for line in part.splitlines() if line.strip()]
        if not lines:
            continue

        start_date, end_date = _extract_date_range(part)
        project_date = " - ".join([item for item in [start_date, end_date] if item])
        title = lines[0]
        if ":" in title:
            title = title.split(":", 1)[0].strip()
        if " - " in title:
            title = title.split(" - ", 1)[0].strip()

        techs = sorted({normalize_skill_name(skill) for skill in extract_skills_with_skillner(part) if skill})
        description_lines = []
        for line in lines[1:]:
            if line not in {start_date, end_date} and not _is_date_like(line):
                description_lines.append(line)
        description = " ".join(description_lines).strip()

        projects.append(
            {
                "project_title": title,
                "project_desc": description,
                "project_date": project_date,
                "technologies": techs,
                "raw_text": part,
            }
        )

    return projects

def parse_education(text):
    edu = {
        "bachelor_edu": [],
        "master_edu": [],
        "phd_edu": [],
        "other_edu": []
    }
    
    if not text:
        return edu
        
    # Split the section by newlines or bullet points
    parts = re.split(r"[\n•]+", text)
    
    for part in parts:
        part = part.strip()
        if not part: 
            continue
            
        if PHD_PATTERN.search(part):
            edu["phd_edu"].append(part)
        elif MASTER_PATTERN.search(part):
            edu["master_edu"].append(part)
        elif BACHELOR_PATTERN.search(part):
            edu["bachelor_edu"].append(part)
        else:
            edu["other_edu"].append(part)
            
    return edu


def extract_resume_info(text):
    sections = extract_sections(text)
    sections = fix_missing_sections(sections, text)

    full_text = "\n".join(sections.values())
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

    contact_text = text or ""

    combined_contact_text = "\n".join([
        contact_text,
        clean_text(contact_text),
        header_text,
        full_text,
    ])

    email = extract_email(combined_contact_text)
    phone_number = extract_phone_number(combined_contact_text)
    location = extract_location(combined_contact_text)
    urls = _extract_urls(combined_contact_text)
    name = extract_name(header_text or text)
    education_detail = parse_education_detailed(sections.get("education", ""))
    experience_detail = parse_experience_detailed(sections.get("experience", ""))
    project_detail = parse_project_detailed(sections.get("projects", ""))

    return {
        "name": name,
        "contact": {
            "name": name,
            "email": email,
            "phone_number": phone_number,
            "location": location,
            "urls": urls,
        },
        "header": sections.get("header", ""),
        "summary": sections.get("summary", ""),
        "experience": experience_detail,
        "experience_section": sections.get("experience", ""),
        "education": education_detail,
        "education_section": sections.get("education", ""),
        "skills_section": sections.get("skills", ""),
        "projects": project_detail,
        "projects_section": sections.get("projects", ""),
        "certifications": sections.get("certifications", ""),
        "skills": extracted_skills,
        "tools": extracted_skills,
        "extracted_skills": extracted_skills,
        "email": email,
        "phone_number": phone_number,
        "location": location,
        "urls": urls,
        "sections": sections,
    }


def build_resume_context(text):
    """
    Return a deterministic, section-aware view of the resume text.

    This is intentionally lightweight: the AI agent should do the semantic
    extraction, while this layer supplies normalized evidence and structure.
    """
    extracted = extract_resume_info(text)
    sections = extracted.get("sections", {}) or extract_sections(text)

    return {
        "raw_text": text or "",
        "sections": sections,
        "header": sections.get("header", ""),
        "summary": sections.get("summary", ""),
        "experience": extracted.get("experience", []),
        "education": extracted.get("education", {}),
        "skills": extracted.get("skills", []),
        "projects": extracted.get("projects", []),
        "certifications": sections.get("certifications", ""),
        "name_candidates": [extracted.get("name", "")] if extracted.get("name") else [],
        "contact_candidates": {
            "email": extracted.get("email", ""),
            "phone_number": extracted.get("phone_number", ""),
            "location": extracted.get("location", ""),
            "urls": extracted.get("urls", []),
        },
        "skill_candidates": extracted.get("skills", extracted.get("extracted_skills", [])),
        "education_candidates": extracted.get("education", {}),
        "experience_candidates": extracted.get("experience", []),
        "project_candidates": extracted.get("projects", []),
    }
