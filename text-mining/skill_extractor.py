import re

SKILLNER_AVAILABLE = False
skill_extractor = None

try:
    import spacy
    from spacy.matcher import PhraseMatcher
    from skillNer.skill_extractor_class import SkillExtractor
    from skillNer.general_params import SKILL_DB

    # Load spaCy model
    nlp = spacy.load("en_core_web_lg")

    # Initialize SkillNer
    skill_extractor = SkillExtractor(
        nlp,
        SKILL_DB,
        PhraseMatcher
    )
    SKILLNER_AVAILABLE = True
except Exception:
    SKILLNER_AVAILABLE = False


NOISE_SKILLS = {
    "a", "b", "c", "d", "e",
    "com", "gmail", "email", "mail",
    "article", "blog", "track", "targets",
    "managed", "collaborated", "including",
    "best practices", "problem solve", "teamwork",
}

GENERIC_STOPWORDS = {
    "and", "or", "the", "a", "an", "to", "for", "of", "in", "on", "with",
}

TECH_KEYWORDS = {
    "sql", "mysql", "postgresql", "oracle", "mongodb", "database", "etl", "ssis", "ssrs",
    "python", "java", "javascript", "typescript", "react", "node", "graphql", "spring",
    "docker", "kubernetes", "aws", "azure", "gcp", "linux", "unix", "redis", "kafka",
    "tensorflow", "pytorch", "machine learning", "data science", "data modeling", "pl sql",
}


def _normalize_skill(skill):
    skill = skill.strip().lower()
    skill = re.sub(r"\s+", " ", skill)
    return skill


def _is_noise_skill(skill):
    norm = _normalize_skill(skill)

    if not norm:
        return True

    if len(norm) == 1:
        return True

    if norm in NOISE_SKILLS:
        return True

    if "@" in norm:
        return True

    words = norm.split()
    if words and all(word in GENERIC_STOPWORDS for word in words):
        return True

    return False


def _append_skill(skills, seen, value):
    if not isinstance(value, str):
        return

    norm = _normalize_skill(value)
    if _is_noise_skill(norm):
        return

    if norm not in seen:
        seen.add(norm)
        skills.append(norm)


def _safe_score(item):
    if not isinstance(item, dict):
        return 1.0

    raw = item.get("score", 1.0)
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 1.0


def _fallback_extract_skills(text):
    skills = []
    seen = set()

    parts = re.split(r"[,\n;/|•]+", text.lower())
    for raw in parts:
        phrase = _normalize_skill(re.sub(r"[^a-z0-9+#.\-\s]", " ", raw))
        if not phrase:
            continue

        words = phrase.split()
        if len(words) > 4:
            continue

        if _is_noise_skill(phrase):
            continue

        if any(keyword in phrase for keyword in TECH_KEYWORDS):
            _append_skill(skills, seen, phrase)

    token_pattern = (
        r"\b(sql|mysql|postgresql|oracle|mongodb|python|java|javascript|typescript|react|node\.js|"
        r"docker|kubernetes|aws|azure|linux|unix|redis|kafka|tensorflow|pytorch|etl|ssis|ssrs|"
        r"machine learning|data science|data modeling|pl sql)\b"
    )

    for match in re.findall(token_pattern, text.lower()):
        _append_skill(skills, seen, match)

    return sorted(skills)


def extract_skills_with_skillner(text, include_ngram=True, ngram_min_score=0.75):
    """
    Extract skills from resume text using SkillNer.
    """

    if not text or not text.strip():
        return []

    if not SKILLNER_AVAILABLE or skill_extractor is None:
        return _fallback_extract_skills(text)

    annotations = skill_extractor.annotate(text)

    results = annotations.get("results", {})
    skills = []
    seen = set()

    # Exact skill matches
    full_matches = results.get("full_matches", [])
    for item in full_matches:
        if isinstance(item, dict):
            _append_skill(skills, seen, item.get("doc_node_value", ""))

    # Partial / scored skill matches
    if include_ngram:
        ngram_matches = results.get("ngram_scored", [])
        for item in ngram_matches:
            if isinstance(item, dict) and _safe_score(item) >= ngram_min_score:
                _append_skill(skills, seen, item.get("doc_node_value", ""))

    skills = sorted(skills)

    return skills