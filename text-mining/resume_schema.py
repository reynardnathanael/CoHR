from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError


class Contact(BaseModel):
    name: Optional[str] = ""
    email: Optional[str] = ""
    phone_number: Optional[str] = ""
    location: Optional[str] = ""
    urls: List[str] = Field(default_factory=list)


class BachelorEducation(BaseModel):
    bachelor_university: Optional[str] = ""
    bachelor_degree: Optional[str] = ""
    bachelor_major: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    details: List[str] = Field(default_factory=list)
    raw_text: Optional[str] = ""


class MasterEducation(BaseModel):
    master_university: Optional[str] = ""
    master_degree: Optional[str] = ""
    master_major: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    details: List[str] = Field(default_factory=list)
    raw_text: Optional[str] = ""


class PhDEducation(BaseModel):
    phd_university: Optional[str] = ""
    phd_degree: Optional[str] = ""
    phd_major: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    details: List[str] = Field(default_factory=list)
    raw_text: Optional[str] = ""


class OtherEducation(BaseModel):
    other_text: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    details: List[str] = Field(default_factory=list)
    raw_text: Optional[str] = ""


class EducationBuckets(BaseModel):
    bachelor_edu: List[BachelorEducation] = Field(default_factory=list)
    master_edu: List[MasterEducation] = Field(default_factory=list)
    phd_edu: List[PhDEducation] = Field(default_factory=list)
    other_edu: List[OtherEducation] = Field(default_factory=list)


class ExperienceEntry(BaseModel):
    experience_title: Optional[str] = ""
    experience_description: Optional[str] = ""
    experience_date: Optional[str] = ""
    company: Optional[str] = ""
    location: Optional[str] = ""
    details: List[str] = Field(default_factory=list)
    raw_text: Optional[str] = ""


class ProjectEntry(BaseModel):
    project_title: Optional[str] = ""
    project_desc: Optional[str] = ""
    project_date: Optional[str] = ""
    details: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    raw_text: Optional[str] = ""


class ResumeSchema(BaseModel):
    contact: Contact = Field(default_factory=Contact)
    summary: Optional[str] = ""
    skills: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    education: EducationBuckets = Field(default_factory=EducationBuckets)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    confidence: Dict[str, float] = Field(default_factory=dict)
    raw_text: Optional[str] = ""


def validate_resume_schema(data: Dict[str, Any]) -> Dict[str, Any]:
    base = {
        "contact": {},
        "summary": "",
        "skills": [],
        "tools": [],
        "education": {
            "bachelor_edu": [],
            "master_edu": [],
            "phd_edu": [],
            "other_edu": [],
        },
        "experience": [],
        "projects": [],
        "certifications": [],
        "languages": [],
        "confidence": {},
        "raw_text": "",
    }
    merged = dict(base)
    merged.update(data or {})

    try:
        if hasattr(ResumeSchema, "model_validate"):
            model = ResumeSchema.model_validate(merged)
            validated = model.model_dump()
        else:
            model = ResumeSchema.parse_obj(merged)
            validated = model.dict()
        merged.update(validated)
        return merged
    except ValidationError:
        return merged
