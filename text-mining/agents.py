import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from extractor import (
    build_resume_context,
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


def _ensure_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _looks_like_education_noise(text: str) -> bool:
    lowered = (text or "").lower().strip()
    if not lowered:
        return True
    if re.search(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b", lowered) or re.search(r"\b\d{4}\b", lowered):
        return True
    if any(keyword in lowered for keyword in ["university", "college", "institute", "school", "academy", "advisor", "research focus"]):
        return True
    return False


def _ensure_education(value: Any) -> Dict[str, List[str]]:
    empty = {
        "bachelor_edu": [],
        "master_edu": [],
        "phd_edu": [],
        "other_edu": [],
    }
    if isinstance(value, dict):
        for key in empty:
            bucket = value.get(key, [])
            if isinstance(bucket, list):
                cleaned_bucket = []
                for item in bucket:
                    if isinstance(item, dict):
                        cleaned_bucket.append(item)
                    elif str(item).strip():
                        text = str(item).strip()
                        if not _looks_like_education_noise(text):
                            cleaned_bucket.append({"raw_text": text})
                empty[key] = cleaned_bucket
            elif isinstance(bucket, dict):
                empty[key] = [bucket]
            elif isinstance(bucket, str) and bucket.strip():
                text = bucket.strip()
                if not _looks_like_education_noise(text):
                    empty[key] = [{"raw_text": text}]
    elif isinstance(value, list):
        cleaned_bucket = []
        for item in value:
            if isinstance(item, dict):
                cleaned_bucket.append(item)
            elif str(item).strip():
                text = str(item).strip()
                if not _looks_like_education_noise(text):
                    cleaned_bucket.append({"raw_text": text})
        empty["other_edu"] = cleaned_bucket
    elif isinstance(value, str) and value.strip():
        text = value.strip()
        if not _looks_like_education_noise(text):
            empty["other_edu"] = [{"raw_text": text}]
    return empty


def _ensure_entry_list(value: Any) -> List[Dict[str, Any]]:
    if isinstance(value, list):
        cleaned = []
        for item in value:
            if isinstance(item, dict):
                cleaned.append(item)
            elif str(item).strip():
                cleaned.append({"raw_text": str(item).strip()})
        return cleaned
    if isinstance(value, dict):
        return [value]
    if isinstance(value, str) and value.strip():
        return [{"raw_text": value.strip()}]
    return []


def _normalize_skill_list(values: Any) -> List[str]:
    normalized = []
    seen = set()
    for item in _ensure_list(values):
        skill = normalize_skill_name(item)
        if skill and skill not in seen:
            seen.add(skill)
            normalized.append(skill)
    return sorted(normalized)


def _extract_evidence_lines(*values: Any) -> List[str]:
    evidence = []
    seen = set()
    for value in values:
        if isinstance(value, str):
            chunks = re.split(r"[\n•;]+", value)
        elif isinstance(value, list):
            chunks = value
        else:
            chunks = []
        for chunk in chunks:
            text = str(chunk).strip()
            if text and text not in seen:
                seen.add(text)
                evidence.append(text)
    return evidence[:12]


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
    context = build_resume_context(text)
    skills = extracted.get("skills", extracted.get("extracted_skills", [])) or []
    normalized_text = (text or "").lower()
    education = extracted.get("education", {}) or {}
    sections = context.get("sections", {}) or {}

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

    tools = extract_tools(normalized_text, list(skills)) or list(skills)
    experience_entries = _ensure_entry_list(extracted.get("experience", []))
    project_entries = _ensure_entry_list(extracted.get("projects", []))
    education_entries = _ensure_education(education)
    certifications_text = extracted.get("certifications", "")

    return {
        "contact": extracted.get("contact", {}),
        "name": extracted.get("name", ""),
        "summary": extracted.get("summary", ""),
        "skills": sorted({normalize_skill_name(skill) for skill in skills if skill}),
        "tools": sorted({normalize_skill_name(skill) for skill in tools if skill}),
        "education": education_entries,
        "experience": experience_entries,
        "projects": project_entries,
        "certifications": _ensure_list(certifications_text),
        "achievements": [],
        "languages": [],
        "personal_identifiers_removed": True,
        "missing_sections": [],
        "confidence_scores": {
            "skills": 0.7 if skills else 0.0,
            "tools": 0.6 if tools else 0.0,
            "education": 0.6 if any(education_entries.values()) else 0.0,
            "experience": 0.6 if experience_entries else 0.0,
            "projects": 0.5 if project_entries else 0.0,
            "certifications": 0.4 if certifications_text else 0.0,
            "languages": 0.0,
        },
        "parsing_notes": [
            "Deterministic fallback parser built from section extraction.",
        ],
        "warnings": [],
        "evidence": {
            "header": context.get("header", ""),
            "sections": sections,
            "contact_candidates": context.get("contact_candidates", {}),
            "skill_candidates": context.get("skill_candidates", []),
        },
    }


def _merge_agent_output(base: Dict[str, Any], parsed: Dict[str, Any]) -> Dict[str, Any]:
    output = dict(base)
    for key in output.keys():
        if key in parsed:
            output[key] = parsed[key]
    return output


def _normalize_resume_output(base: Dict[str, Any], parsed: Dict[str, Any]) -> Dict[str, Any]:
    merged = _merge_agent_output(base, parsed)
    contact = merged.get("contact", {})
    if not isinstance(contact, dict):
        contact = {
            "name": merged.get("name", ""),
            "email": merged.get("email", ""),
            "phone_number": merged.get("phone_number", ""),
            "location": merged.get("location", ""),
            "urls": merged.get("urls", []),
        }
    contact["name"] = str(contact.get("name", merged.get("name", ""))).strip()
    contact["email"] = str(contact.get("email", merged.get("email", ""))).strip()
    contact["phone_number"] = str(contact.get("phone_number", merged.get("phone_number", ""))).strip()
    contact["location"] = str(contact.get("location", merged.get("location", ""))).strip()
    contact["urls"] = _ensure_list(contact.get("urls", []))
    merged["contact"] = contact
    merged["summary"] = str(merged.get("summary", "")).strip()
    merged["skills"] = _normalize_skill_list(merged.get("skills", []))
    merged["tools"] = _normalize_skill_list(merged.get("tools", []))
    merged["education"] = _ensure_education(merged.get("education", {}))
    merged["experience"] = _ensure_entry_list(merged.get("experience", []))
    merged["projects"] = _ensure_entry_list(merged.get("projects", []))
    merged["certifications"] = _ensure_list(merged.get("certifications", []))
    merged["achievements"] = _ensure_list(merged.get("achievements", []))
    merged["languages"] = _ensure_list(merged.get("languages", []))
    merged["missing_sections"] = _ensure_list(merged.get("missing_sections", []))
    merged["warnings"] = _ensure_list(merged.get("warnings", []))
    merged["parsing_notes"] = _ensure_list(merged.get("parsing_notes", []))
    merged["confidence_scores"] = {
        key: float(value)
        for key, value in dict(merged.get("confidence_scores", {})).items()
        if isinstance(value, (int, float))
    }
    merged["field_evidence"] = dict(merged.get("field_evidence", {}))
    return merged


def parse_resume_agent(
    text: str,
    *,
    model: Optional[str] = None,
    retries: int = 2,
    deterministic_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    base = _fallback_resume_schema(text)
    education = base.get("education", {}) if isinstance(base.get("education"), dict) else {}
    contact = base.get("contact", {}) if isinstance(base.get("contact"), dict) else {}
    base["missing_sections"] = []
    if not any(str(contact.get(key, "")).strip() for key in ["name", "email", "phone_number", "location"]):
        base["missing_sections"].append("contact")
    if not str(base.get("summary", "")).strip():
        base["missing_sections"].append("summary")
    if not base.get("skills"):
        base["missing_sections"].append("skills")
    if not any(education.get(bucket) for bucket in ["bachelor_edu", "master_edu", "phd_edu", "other_edu"]):
        base["missing_sections"].append("education")
    if not base.get("experience"):
        base["missing_sections"].append("experience")
    if not base.get("projects"):
        base["missing_sections"].append("projects")
    if not base.get("certifications"):
        base["missing_sections"].append("certifications")
    if not base.get("languages"):
        base["missing_sections"].append("languages")
    context = build_resume_context(text)
    evidence_text = "\n".join(
        _extract_evidence_lines(
            context.get("header", ""),
            context.get("summary", ""),
            context.get("skills", ""),
            context.get("experience", ""),
            context.get("projects", ""),
            context.get("certifications", ""),
            list(context.get("skill_candidates", [])),
        )
    )
    prompt = f"""
You are a resume information extraction agent.
Extract the resume into strict JSON with these keys:
contact, summary, skills, tools, education, experience, projects,
certifications, languages, personal_identifiers_removed, missing_sections,
confidence_scores, parsing_notes, warnings, field_evidence

Rules:
- Use the provided evidence and section candidates as your source of truth.
- Preserve factual content only. Do not invent details.
- Put programming languages, frameworks, databases, cloud/devops tools, IDEs, and libraries in skills.
- `tools` may mirror `skills` for backward compatibility.
- Use arrays for list fields. Use structured objects for education, experience, and projects.
- Education objects must use bucket-specific keys such as `bachelor_university`, `master_university`, `phd_university`, plus `start_date`, `end_date`, `degree`, `major`, `details`, and `raw_text`.
- Experience objects must use `experience_title`, `experience_description`, `experience_date`, `company`, `location`, and `raw_text`.
- Project objects must use `project_title`, `project_desc`, `project_date`, `technologies`, and `raw_text`.
- Put university names and date ranges inside the correct education bucket entry. `other_edu` is only for genuinely uncategorized education facts, not university names, date ranges, or advisor/research-focus lines.
- confidence_scores must be numbers between 0 and 1.
- field_evidence should map each field to short source snippets.
- If a value is absent, return an empty string or empty array as appropriate.
- Return JSON only.

Evidence and section candidates:
{json.dumps(context, ensure_ascii=True)}

Resume text:
{text}

Candidate evidence snippets:
{evidence_text}
""".strip()

    if not ollama_available():
        fallback = dict(deterministic_info or base)
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
                merged = _normalize_resume_output(base, parsed)
                merged["name"] = str(merged.get("name", "")).strip()
                merged["email"] = str(merged.get("email", "")).strip()
                merged["phone_number"] = str(merged.get("phone_number", "")).strip()
                merged["location"] = str(merged.get("location", "")).strip()
                merged["missing_sections"] = merged.get("missing_sections", base.get("missing_sections", []))
                merged["parsing_notes"] = [
                    *base.get("parsing_notes", []),
                    *(_listify(merged.get("parsing_notes", []))),
                ]
                merged["warnings"] = _listify(merged.get("warnings", []))
                merged["field_evidence"] = {
                    **dict(base.get("evidence", {})),
                    **dict(merged.get("field_evidence", {})),
                }
                if deterministic_info:
                    merged.setdefault("deterministic_info", deterministic_info)
                return merged
            last_error = "Invalid JSON returned by the model."
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            last_error = str(exc)

    fallback = dict(deterministic_info or base)
    fallback["parsing_notes"] = [
        *base.get("parsing_notes", []),
        "Failed to parse LLM output; used fallback parser.",
    ]
    fallback["warnings"] = [last_error] if last_error else []
    fallback["field_evidence"] = dict(base.get("evidence", {}))
    if deterministic_info:
        fallback.setdefault("deterministic_info", deterministic_info)
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
        flattened = []
        for item in value:
            if isinstance(item, dict):
                text = " ".join(
                    str(v).strip()
                    for v in item.values()
                    if str(v).strip()
                ).strip()
                if text:
                    flattened.append(text)
            else:
                text = str(item).strip()
                if text:
                    flattened.append(text)
        return flattened
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
    skills = resume.get("skills", resume.get("extracted_skills", []))
    if not skills and isinstance(resume.get("llm_resume"), dict):
        skills = resume["llm_resume"].get("skills", [])
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
Candidate Resume: {json.dumps({
    "name": resume.get("name", ""),
    "skills": skills,
    "education": education,
    "experience": experience,
    "projects": projects,
    "certifications": certifications,
    "full_text": resume.get("full_text", resume.get("experience", "")),
    "llm_resume": resume.get("llm_resume", {}),
}, ensure_ascii=True)}

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
