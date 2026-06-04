import re
import nltk

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from extractor import extract_skills_with_skillner, normalize_skill_name


nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)

STOPWORDS = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

_model = None
_model_error = None


def _load_embedding_model():
    global _model, _model_error

    if _model is not None or _model_error is not None:
        return _model

    try:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as exc:
        _model_error = exc
        _model = None

    return _model


def _encode_texts(texts):
    model = _load_embedding_model()
    if model is not None:
        return model.encode(texts)

    vectorizer = TfidfVectorizer(stop_words="english")
    return vectorizer.fit_transform(texts)


SECTION_WEIGHTS = {
    "experience": 4,
    "projects": 3,
    "skills_section": 3,
    "summary": 2,
    "certifications": 2,
    "education": 1,
}


def clean_skill(skill):
    return normalize_skill_name(skill)


def tokenize(text):
    if not text:
        return []

    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]*", text.lower())

    tokens = []
    for word in words:
        if word not in STOPWORDS and len(word) > 2:
            tokens.append(lemmatizer.lemmatize(word))

    return tokens


def build_weighted_candidate_text(resume):
    """
    Build candidate profile text with weighted sections.

    Experience is repeated more times because it should matter more
    than education for job matching.
    """

    parts = []

    def flatten_text(value):
        if isinstance(value, dict):
            flattened = []
            for bucket in value.values():
                if isinstance(bucket, list):
                    flattened.extend(str(item).strip() for item in bucket if str(item).strip())
                elif isinstance(bucket, str) and bucket.strip():
                    flattened.append(bucket.strip())
            return " ".join(flattened)

        if isinstance(value, list):
            return " ".join(str(item).strip() for item in value if str(item).strip())

        return str(value).strip() if value else ""

    for section, weight in SECTION_WEIGHTS.items():
        text = flatten_text(resume.get(section, ""))

        if text:
            parts.extend([text] * weight)

    skills = resume.get("extracted_skills", [])

    if isinstance(skills, list):
        skills_text = " ".join(skills)
        parts.extend([skills_text] * 3)

    return " ".join(parts)


def calculate_skill_overlap(job_skills, candidate_skills):
    job_skills = {clean_skill(skill) for skill in job_skills}
    candidate_skills = {clean_skill(skill) for skill in candidate_skills}

    if not job_skills:
        return 0.0, []

    matched_skills = sorted(job_skills.intersection(candidate_skills))

    score = len(matched_skills) / len(job_skills)

    return score, matched_skills


def calculate_similarity(
    job_description,
    resumes,
    embedding_weight=0.30,
    skill_weight=0.55
):
    """
    Hybrid score:

    Final score =
    55% SBERT semantic similarity
    + 45% normalized skill overlap

    SBERT compares the overall meaning of the job description and candidate.
    Skill overlap checks whether the candidate has the required technical skills.
    It is weighted higher because short job descriptions are usually mostly
    requirements, while resume embeddings can over-reward generally similar CVs.
    """

    job_skills = extract_skills_with_skillner(job_description)

    for resume in resumes:
        candidate_text = build_weighted_candidate_text(resume)

        embeddings = _encode_texts([job_description, candidate_text])
        job_embedding = embeddings[0:1]
        candidate_embedding = embeddings[1:2]

        embedding_score = cosine_similarity(
            job_embedding,
            candidate_embedding
        )[0][0]

        skill_score, matched_skills = calculate_skill_overlap(
            job_skills,
            resume.get("extracted_skills", [])
        )

        final_score = (
            embedding_weight * embedding_score
            + skill_weight * skill_score
        )

        resume["embedding_score"] = round(float(embedding_score) * 100, 2)
        resume["skill_score"] = round(float(skill_score) * 100, 2)
        resume["similarity_score"] = round(float(final_score) * 100, 2)
        resume["matched_skills"] = matched_skills
        resume["job_skills"] = job_skills

    ranked_resumes = sorted(
        resumes,
        key=lambda x: x["similarity_score"],
        reverse=True
    )

    return ranked_resumes
