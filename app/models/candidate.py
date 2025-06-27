from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary, Float, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False)
    resume_filename = Column(String)
    resume_data = Column(LargeBinary)  # Store PDF as binary
    
    # Scores from resume screening
    skills_match_score = Column(Float)  # Out of 10
    resume_relevancy_score = Column(Float)  # Out of 10
    job_description_relevancy_score = Column(Float)  # Out of 10
    
    # Q&A document
    qa_document_filename = Column(String)
    qa_document_data = Column(LargeBinary)  # Store PDF as binary
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="candidates")