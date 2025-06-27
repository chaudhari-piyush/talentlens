from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class JobBase(BaseModel):
    job_name: str
    job_description: str
    expected_skills: List[str]


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    job_name: Optional[str] = None
    job_description: Optional[str] = None
    expected_skills: Optional[List[str]] = None


class JobResponse(JobBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True