import math
import re
from collections import Counter

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "in",
    "is", "it", "of", "on", "or", "that", "the", "to", "was", "were", "with",
}


def _tokenize(text):
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]*", text.lower())
    return [word for word in words if word not in STOPWORDS]


def _cosine_counter(a, b):
    if not a or not b:
        return 0.0

    keys = set(a) & set(b)
    dot = sum(a[key] * b[key] for key in keys)
    norm_a = math.sqrt(sum(value * value for value in a.values()))
    norm_b = math.sqrt(sum(value * value for value in b.values()))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (norm_a * norm_b)


def calculate_similarity(job_description, resumes):
    if SKLEARN_AVAILABLE:
        documents = [job_description] + [resume["full_text"] for resume in resumes]

        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2)
        )

        tfidf_matrix = vectorizer.fit_transform(documents)

        job_vector = tfidf_matrix[0]
        resume_vectors = tfidf_matrix[1:]

        scores = cosine_similarity(job_vector, resume_vectors).flatten()
    else:
        job_vector = Counter(_tokenize(job_description))
        scores = []
        for resume in resumes:
            resume_vector = Counter(_tokenize(resume["full_text"]))
            scores.append(_cosine_counter(job_vector, resume_vector))

    for resume, score in zip(resumes, scores):
        resume["similarity_score"] = round(score * 100, 2)

    ranked_resumes = sorted(
        resumes,
        key=lambda x: x["similarity_score"],
        reverse=True
    )

    return ranked_resumes