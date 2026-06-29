from __future__ import annotations

from typing import Any, Dict, List

from extractor import normalize_skill_name


def _as_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _as_dict_list(value: Any) -> List[Dict[str, Any]]:
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


def _pick_non_empty(*values: Any) -> Any:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, list) and value:
            return value
        if isinstance(value, dict) and value:
            return value
    return ""


def merge_resume_outputs(deterministic_info, llm_info, raw_text):
    """
    Merge old extractor output with LLM output safely.
    """
    deterministic_info = dict(deterministic_info or {})
    llm_info = dict(llm_info or {})

    merged = dict(deterministic_info)
    merged["raw_text"] = raw_text or merged.get("raw_text", "")

    deterministic_contact = deterministic_info.get("contact", {})
    if not isinstance(deterministic_contact, dict):
        deterministic_contact = {
            "name": deterministic_info.get("name", ""),
            "email": deterministic_info.get("email", ""),
            "phone_number": deterministic_info.get("phone_number", ""),
            "location": deterministic_info.get("location", ""),
            "urls": _as_list(deterministic_info.get("urls", [])),
        }
    llm_contact = llm_info.get("contact", {}) if isinstance(llm_info.get("contact"), dict) else {}
    merged["contact"] = {
        "name": _pick_non_empty(deterministic_contact.get("name"), llm_contact.get("name", "")),
        "email": deterministic_contact.get("email", llm_contact.get("email", "")),
        "phone_number": deterministic_contact.get("phone_number", llm_contact.get("phone_number", "")),
        "location": deterministic_contact.get("location", llm_contact.get("location", "")),
        "urls": _as_list(deterministic_contact.get("urls", [])) or _as_list(llm_contact.get("urls", [])),
    }

    summary = llm_info.get("summary", "")
    if not isinstance(summary, str) or not summary.strip():
        summary = deterministic_info.get("summary", "")
    merged["summary"] = summary

    deterministic_skills = _as_list(deterministic_info.get("skills", deterministic_info.get("extracted_skills", [])))
    llm_skills = _as_list(llm_info.get("skills", []))
    skills = []
    seen = set()
    for skill in deterministic_skills + llm_skills:
        normalized = normalize_skill_name(skill)
        if normalized and normalized not in seen:
            seen.add(normalized)
            skills.append(normalized)
    merged["skills"] = skills
    merged["extracted_skills"] = skills

    def _merge_buckets(base, override):
        base = base if isinstance(base, dict) else {}
        override = override if isinstance(override, dict) else {}
        merged_buckets = {}
        for key in ["bachelor_edu", "master_edu", "phd_edu", "other_edu"]:
            base_items = _as_dict_list(base.get(key))
            override_items = _as_dict_list(override.get(key))
            if key == "other_edu":
                merged_buckets[key] = base_items or [item for item in override_items if str(item.get("raw_text", "")).strip()]
            else:
                merged_buckets[key] = base_items or override_items
        return merged_buckets

    llm_education = llm_info.get("education", {})
    merged["education"] = _merge_buckets(deterministic_info.get("education", {}), llm_education)

    llm_experience = _as_dict_list(llm_info.get("experience", []))
    merged["experience"] = llm_experience if llm_experience else _as_dict_list(deterministic_info.get("experience", []))

    llm_projects = _as_dict_list(llm_info.get("projects", []))
    merged["projects"] = llm_projects if llm_projects else _as_dict_list(deterministic_info.get("projects", []))

    llm_certifications = llm_info.get("certifications", [])
    merged["certifications"] = llm_certifications if llm_certifications else deterministic_info.get("certifications", [])

    llm_languages = llm_info.get("languages", [])
    merged["languages"] = _as_list(llm_languages) if llm_languages else _as_list(deterministic_info.get("languages", []))

    confidence = dict(deterministic_info.get("confidence_scores", {}) or {})
    confidence.update(dict(llm_info.get("confidence_scores", {}) or {}))
    if not confidence:
        education_present = bool(
            merged.get("education")
            and any(merged["education"].get(bucket) for bucket in ["bachelor_edu", "master_edu", "phd_edu", "other_edu"])
        )
        confidence = {
            "contact": 0.6 if merged["contact"] else 0.0,
            "summary": 0.5 if merged.get("summary") else 0.0,
            "skills": 0.6 if merged.get("skills") else 0.0,
            "education": 0.5 if education_present else 0.0,
            "experience": 0.5 if merged.get("experience") else 0.0,
            "projects": 0.5 if merged.get("projects") else 0.0,
            "certifications": 0.4 if merged.get("certifications") else 0.0,
            "languages": 0.3 if merged.get("languages") else 0.0,
        }
    merged["confidence"] = confidence
    merged["confidence_scores"] = confidence

    for key in deterministic_info:
        merged.setdefault(key, deterministic_info[key])

    return merged
