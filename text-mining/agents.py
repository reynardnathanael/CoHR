import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from extractor import (
    extract_resume_info,
    extract_skills_with_skillner,
    normalize_skill_name,
)


DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

TOOL_ALIASES = {
    "python": "python",
    "java": "java",
    "javascript": "javascript",
    "typescript": "typescript",
    "sql": "sql",
    "mysql": "mysql",
    "postgresql": "postgresql",
    "postgres": "postgresql",
    "oracle": "oracle",
    "mongodb": "mongodb",
    "mongo db": "mongodb",
    "git": "git",
    "github": "github",
    "gitlab": "gitlab",
    "docker": "docker",
    "kubernetes": "kubernetes",
    "aws": "aws",
    "azure": "azure",
    "gcp": "gcp",
    "linux": "linux",
    "unix": "unix",
    "react": "react",
    "node": "node.js",
    "node.js": "node.js",
    "django": "django",
    "flask": "flask",
    "fastapi": "fastapi",
    "spring": "spring",
    "spring boot": "spring boot",
    "numpy": "numpy",
    "pandas": "pandas",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "tensorflow": "tensorflow",
    "pytorch": "pytorch",
    "power bi": "power bi",
    "tableau": "tableau",
    "airflow": "airflow",
    "spark": "spark",
    "hadoop": "hadoop",
    "vscode": "vscode",
    "vs code": "vscode",
    "visual studio code": "vscode",
    "intellij": "intellij idea",
    "intellij idea": "intellij idea",
    "pycharm": "pycharm",
    "jupyter": "jupyter notebook",
    "jupyter notebook": "jupyter notebook",
    "jira": "jira",
    "confluence": "confluence",
    "jenkins": "jenkins",
    "terraform": "terraform",
    "ansible": "ansible",
    "html": "html",
    "css": "css",
    "bootstrap": "bootstrap",
    "tailwind": "tailwind css",
}

TOOL_PATTERNS = [
    (r"\bnode\.js\b", "node.js"),
    (r"\bscikit-learn\b", "scikit-learn"),
    (r"\bvs code\b", "vscode"),
    (r"\bvisual studio code\b", "vscode"),
    (r"\bjupyter notebook\b", "jupyter notebook"),
    (r"\bspring boot\b", "spring boot"),
    (r"\bmongo db\b", "mongodb"),
]


def _safe_json_loads(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None

    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return None

        try:
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None


def ollama_available() -> bool:
    try:
        # Check the base URL to see if the Ollama service is alive
        # This is much faster than doing a full "ping" generation which can timeout.
        base_url = OLLAMA_URL.replace("/api/generate", "")
        request = urllib.request.Request(base_url, method="GET")
        with urllib.request.urlopen(request, timeout=3) as response:
            return response.status == 200
    except Exception:
        return False


def call_ollama(prompt: str, *, system: str = "", model: Optional[str] = None) -> str:
    payload = {
        "model": model or DEFAULT_OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    if system:
        payload["system"] = system

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
        return data.get("response", "")


def _fallback_resume_schema(text: str) -> Dict[str, Any]:
    extracted = extract_resume_info(text)
    skills = extracted.get("extracted_skills", []) or []
    normalized_text = (text or "").lower()
    education = extracted.get("education", {}) or {}

    def normalize_education_bucket(value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []

    def split_items(value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            parts = re.split(r"[•\n;/|,]+", value)
            return [part.strip() for part in parts if part.strip()]
        return []

    def extract_tools(source_text: str, extra_values: List[str]) -> List[str]:
        found = []
        seen = set()

        def add_tool(value: str):
            tool = normalize_skill_name(value)
            if tool and tool not in seen:
                seen.add(tool)
                found.append(tool)

        for tool in extra_values:
            key = normalize_skill_name(tool)
            if key in TOOL_ALIASES:
                add_tool(TOOL_ALIASES[key])

        for alias, canonical in TOOL_ALIASES.items():
            if re.search(rf"(?<![a-z0-9+#.]){re.escape(alias)}(?![a-z0-9+#.])", source_text):
                add_tool(canonical)

        for pattern, canonical in TOOL_PATTERNS:
            if re.search(pattern, source_text):
                add_tool(canonical)

        return sorted(found)

    tools = extract_tools(normalized_text, list(skills))

    return {
        "skills": sorted({normalize_skill_name(skill) for skill in skills if skill}),
        "tools": tools,
        "education": {
            "bachelor_edu": normalize_education_bucket(education.get("bachelor_edu")),
            "master_edu": normalize_education_bucket(education.get("master_edu")),
            "phd_edu": normalize_education_bucket(education.get("phd_edu")),
            "other_edu": normalize_education_bucket(education.get("other_edu")),
        },
        "experience": split_items(extracted.get("experience", "")),
        "projects": split_items(extracted.get("projects", "")),
        "certifications": split_items(extracted.get("certifications", "")),
        "achievements": [],
        "languages": [],
        "personal_identifiers_removed": True,
        "missing_sections": [],
        "confidence_scores": {
            "skills": 0.7 if skills else 0.0,
            "tools": 0.6 if tools else 0.0,
            "education": 0.6 if extracted.get("education") else 0.0,
            "experience": 0.6 if extracted.get("experience") else 0.0,
            "projects": 0.5 if extracted.get("projects") else 0.0,
            "certifications": 0.4 if extracted.get("certifications") else 0.0,
            "languages": 0.0,
        },
        "parsing_notes": [
            "Deterministic fallback parser built from section extraction.",
        ],
        "warnings": [],
    }


def _merge_agent_output(base: Dict[str, Any], parsed: Dict[str, Any]) -> Dict[str, Any]:
    output = dict(base)
    for key in output.keys():
        if key in parsed:
            output[key] = parsed[key]
    return output


def parse_resume_agent(text: str, *, model: Optional[str] = None, retries: int = 2) -> Dict[str, Any]:
    base = _fallback_resume_schema(text)
    base["missing_sections"] = [
        section
        for section in ["skills", "tools", "education", "experience", "projects", "certifications", "languages"]
        if not base.get(section)
    ]
    prompt = f"""
Extract resume data as strict JSON with these keys:
skills, tools, education, experience, projects, certifications,
achievements, languages, personal_identifiers_removed, missing_sections,
confidence_scores, parsing_notes, warnings

Rules:
- Preserve the factual content from the resume sections.
- Put programming languages, frameworks, databases, cloud/devops tools, IDEs, and libraries in tools.
- If a section is missing, keep it as an empty array.
- confidence_scores must be numbers between 0 and 1.
- missing_sections must list any absent major sections.
- Use arrays for list fields.
- Return JSON only.

Resume text:
{text}
""".strip()

    if not ollama_available():
        fallback = dict(base)
        fallback["parsing_notes"] = [
            "Ollama unavailable; used deterministic fallback parser.",
            *fallback.get("parsing_notes", []),
        ]
        return fallback

    last_error = ""
    for _ in range(max(1, retries)):
        try:
            raw = call_ollama(prompt, system="You are a precise resume parsing assistant.", model=model)
            parsed = _safe_json_loads(raw)
            if parsed:
                merged = _merge_agent_output(base, parsed)
                merged["missing_sections"] = merged.get("missing_sections", base.get("missing_sections", []))
                merged["parsing_notes"] = [
                    *base.get("parsing_notes", []),
                    *(_listify(merged.get("parsing_notes", []))),
                ]
                merged["warnings"] = _listify(merged.get("warnings", []))
                return merged
            last_error = "Invalid JSON returned by the model."
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            last_error = str(exc)

    fallback = dict(base)
    fallback["parsing_notes"] = [
        *base.get("parsing_notes", []),
        "Failed to parse LLM output; used fallback parser.",
    ]
    fallback["warnings"] = [last_error] if last_error else []
    return fallback


def build_job_profile(job_description: str, *, model: Optional[str] = None) -> Dict[str, Any]:
    fallback = {
        "must_have_skills": [],
        "preferred_skills": [],
        "experience_level": "",
        "education_requirements": [],
        "responsibilities": [],
        "technologies_tools": [],
    }

    if not job_description:
        return fallback

    if not ollama_available():
        skills = [normalize_skill_name(skill) for skill in extract_skills_with_skillner(job_description)]
        return {
            **fallback,
            "must_have_skills": skills[:8],
            "technologies_tools": skills[:8],
        }

    prompt = f"""
Convert the job description into strict JSON with keys:
must_have_skills, preferred_skills, experience_level,
education_requirements, responsibilities, technologies_tools

Rules:
- Return JSON only.
- Use arrays for list fields.
- Keep skill names short and normalized.

Job description:
{job_description}
""".strip()

    try:
        raw = call_ollama(prompt, system="You are a job description parsing assistant.", model=model)
        parsed = _safe_json_loads(raw)
        if parsed:
            return _merge_agent_output(fallback, parsed)
    except Exception:
        pass

    return fallback


def _listify(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _normalize_education(value: Any) -> Dict[str, List[str]]:
    empty = {
        "bachelor_edu": [],
        "master_edu": [],
        "phd_edu": [],
        "other_edu": [],
    }
    if isinstance(value, dict):
        for key in empty:
            empty[key] = _listify(value.get(key, []))
    elif isinstance(value, list):
        empty["other_edu"] = _listify(value)
    elif isinstance(value, str) and value.strip():
        empty["other_edu"] = [value.strip()]
    return empty


def _score_overlap(required: List[str], candidate: List[str]) -> Dict[str, Any]:
    req = {normalize_skill_name(item) for item in required if item}
    cand = {normalize_skill_name(item) for item in candidate if item}
    matched = sorted(req.intersection(cand))
    missing = sorted(req.difference(cand))
    score = (len(matched) / len(req)) if req else 0.0
    return {"score": score, "matched": matched, "missing": missing}


def screen_candidate(job_profile: Dict[str, Any], resume: Dict[str, Any], *, model: Optional[str] = None) -> Dict[str, Any]:
    # 1. FALLBACK MATH LOGIC (Used if Ollama is down)
    skills = resume.get("extracted_skills", [])
    projects = _listify(resume.get("projects", ""))
    education = _normalize_education(resume.get("education", {}))
    experience = _listify(resume.get("experience", ""))
    certifications = _listify(resume.get("certifications", ""))

    skill_match = _score_overlap(job_profile.get("must_have_skills", []), skills)
    tool_match = _score_overlap(job_profile.get("technologies_tools", []), skills)

    confidence = 0.55 * skill_match["score"] + 0.45 * tool_match["score"]
    fit_category = "Strong Fit" if confidence >= 0.75 else "Potential Fit" if confidence >= 0.45 else "Weak Fit"

    weaknesses = []
    if skill_match["missing"]:
        weaknesses.append(f"Missing core skills: {', '.join(skill_match['missing'][:5])}")
    if not experience:
        weaknesses.append("Experience evidence is thin or missing.")
    if not projects:
        weaknesses.append("No project evidence found.")

    fallback_result = {
        "fit_category": fit_category,
        "score": round(confidence * 100, 2),
        "strengths": skill_match["matched"][:5] + tool_match["matched"][:5],
        "weaknesses": weaknesses,
        "missing_requirements": skill_match["missing"][:8],
        "recommendation": "Advance to human review" if confidence >= 0.45 else "Do not advance automatically",
        "explanation": "Score blends required-skill overlap and tool alignment, with a fallback to human review when evidence is sparse.",
        "confidence": round(confidence, 3),
        "evidence": {
            "experience_present": bool(experience),
            "education_present": any(education.values()),
            "certifications_present": bool(certifications),
            "project_count": len(projects),
        },
    }

    # 2. TRUE AI AGENT LOGIC
    if not ollama_available():
        fallback_result["error"] = "AI Evaluation failed. Used fallback math scoring."
        return fallback_result

    prompt = f"""
You are an elite Senior Technical Recruiter. Evaluate the candidate against the job requirements.

Job Requirements: {json.dumps(job_profile)}
Candidate Resume: {resume.get('full_text', resume.get('experience', ''))}

Based on your reasoning, provide ONLY a valid JSON object with the following exact keys:
- "fit_category": exactly one of "Strong Fit", "Potential Fit", or "Weak Fit".
- "score": a number from 0 to 100 representing your confidence in this candidate.
- "strengths": an array of 3 to 5 strings detailing their strongest matching skills.
- "weaknesses": an array of 2 to 3 strings detailing missing requirements or red flags.
- "recommendation": a short 1-sentence recommendation on whether HR should interview them.
""".strip()

    try:
        raw = call_ollama(prompt, system="You are an expert HR recruiter outputting strict JSON.", model=model)
        parsed = _safe_json_loads(raw)
        if parsed and "score" in parsed and "fit_category" in parsed:
            # Merge the AI insights with the base evidence formatting
            parsed["confidence"] = parsed["score"] / 100.0
            parsed["evidence"] = fallback_result["evidence"]
            return parsed
    except Exception as exc:
        fallback_result["error"] = f"AI Agent error: {str(exc)}. Used fallback math scoring."

    return fallback_result


def generate_summary_agent(
    resume_text: str,
    job_description: str,
    model: Optional[str] = None
) -> str:
    if not ollama_available():
        return "Failed to generate AI summary. Make sure Ollama is running locally."

    prompt = f"""
You are an expert HR assistant. Write a concise, 3-to-4 sentence professional summary of the candidate's background and their potential fit for the role.

Job description:
{job_description}

Resume text:
{resume_text}

Provide ONLY the plain text summary. Do not use bullet points or introductory phrases like "Here is a summary".
""".strip()

    try:
        raw = call_ollama(prompt, system="You are a professional HR assistant.", model=model)
        return raw.strip() if raw else "Summary generation returned empty."
    except Exception as exc:
        return f"Failed to generate summary: {str(exc)}"
