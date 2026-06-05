from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
import datetime
from database import Base

class Profile(Base):
    __tablename__ = "profiles"
    profile_id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    email = Column(Text)
    phone = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Job(Base):
    __tablename__ = "jobs"
    job_id = Column(Integer, primary_key=True, index=True)
    title = Column(Text)
    job_description = Column(Text)
    job_skills = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Resume(Base):
    __tablename__ = "resumes"
    resume_id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.profile_id"))
    raw_text = Column(Text)
    summary = Column(Text)
    bachelor_education = Column(Text)
    master_education = Column(Text)
    phd_education = Column(Text)
    projects = Column(Text)
    experience = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Skill(Base):
    __tablename__ = "skills"
    skill_id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(Text)

class JobSkill(Base):
    __tablename__ = "job_skills"
    job_skill_id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id"))
    skill_id = Column(Integer, ForeignKey("skills.skill_id"))

class ResumeSkill(Base):
    __tablename__ = "resume_skills"
    resume_skill_id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.resume_id"))
    skill_id = Column(Integer, ForeignKey("skills.skill_id"))

class ScreeningResult(Base):
    __tablename__ = "screening_results"
    screening_result_id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id"))
    resume_id = Column(Integer, ForeignKey("resumes.resume_id"))
    fit_category = Column(Text)
    fit_score = Column(Float)
    strengths = Column(Text)
    weakness = Column(Text)
    missing_requirements = Column(Text)
    recommendation = Column(Text)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)