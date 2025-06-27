from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class CandidateBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    job_id: int


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class CandidateResponse(CandidateBase):
    id: int
    resume_filename: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CandidateWithScores(CandidateResponse):
    skills_match_score: Optional[float]
    resume_relevancy_score: Optional[float]
    job_description_relevancy_score: Optional[float]
    qa_document_filename: Optional[str]
    
    class Config:
        from_attributes = True


class ResumeScreeningScores(BaseModel):
    skills_match_score: float
    resume_relevancy_score: float
    job_description_relevancy_score: float