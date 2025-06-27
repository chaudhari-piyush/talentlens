from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
import json
import logging

from app.db.session import get_db
from app.core.auth import get_current_active_user
from app.settings import settings
from app.models.user import User
from app.models.job import Job
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateResponse, CandidateWithScores
from app.core.gemini_service import get_gemini_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=CandidateResponse)
async def create_candidate(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    job_id: int = Form(...),
    resume: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify job exists (any authenticated user can add candidates to any job)
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Validate file type
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Read resume file
    resume_data = await resume.read()
    
    # Create candidate
    candidate = Candidate(
        job_id=job_id,
        name=name,
        email=email,
        phone=phone,
        resume_filename=resume.filename,
        resume_data=resume_data
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    
    # Trigger resume scanning asynchronously
    # This would typically be done via a background task queue
    # For now, we'll make a synchronous call
    try:
        await scan_resume_background(candidate.id, db)
    except Exception as e:
        # Log error but don't fail the candidate creation
        print(f"Error scanning resume: {e}")
    
    return candidate


@router.get("/", response_model=List[CandidateWithScores])
async def list_candidates(
    job_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get all candidates (any authenticated user can see all candidates)
    query = db.query(Candidate)
    
    if job_id:
        # Filter by job_id if provided
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        query = query.filter(Candidate.job_id == job_id)
    
    candidates = query.offset(skip).limit(limit).all()
    return candidates


@router.get("/{candidate_id}", response_model=CandidateWithScores)
async def get_candidate(
    candidate_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get any candidate by ID (any authenticated user can access)
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return candidate


@router.get("/{candidate_id}/resume")
async def download_resume(
    candidate_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get any candidate by ID (any authenticated user can access)
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if not candidate.resume_data:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return Response(
        content=candidate.resume_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{candidate.resume_filename}"'
        }
    )


@router.get("/{candidate_id}/qa-document")
async def download_qa_document(
    candidate_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get any candidate by ID (any authenticated user can access)
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if not candidate.qa_document_data:
        raise HTTPException(status_code=404, detail="Q&A document not yet generated")
    
    return Response(
        content=candidate.qa_document_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{candidate.qa_document_filename}"'
        }
    )


@router.post("/{candidate_id}/rescan")
async def rescan_resume(
    candidate_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get any candidate by ID (any authenticated user can access)
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    try:
        await scan_resume_background(candidate.id, db)
        return {"message": "Resume rescanning initiated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scanning resume: {str(e)}")


@router.delete("/{candidate_id}")
async def delete_candidate(
    candidate_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get any candidate by ID (any authenticated user can access)
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    db.delete(candidate)
    db.commit()
    return {"message": "Candidate deleted successfully"}


async def scan_resume_background(candidate_id: int, db: Session):
    """
    Background task to scan resume and generate Q&A document using Gemini.
    
    This function:
    1. Extracts text from the resume PDF
    2. Fetches job details
    3. Uses Gemini to calculate scoring metrics
    4. Generates interview Q&A using Gemini
    5. Creates a PDF document with the Q&A
    6. Saves everything to the database
    """
    try:
        # Get candidate and job details
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate or not candidate.resume_data:
            logger.error(f"Candidate {candidate_id} not found or has no resume")
            return
        
        job = candidate.job
        if not job:
            logger.error(f"Job not found for candidate {candidate_id}")
            return
        
        # Initialize Gemini service
        try:
            gemini_service = get_gemini_service()
        except ValueError as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            logger.error("Please configure GEMINI_API_KEY in your environment variables")
            return
        
        # Step 1: Extract text from PDF
        logger.info(f"Extracting text from resume for candidate {candidate_id}")
        resume_text = gemini_service.extract_text_from_pdf(candidate.resume_data)
        
        if not resume_text:
            logger.error(f"Failed to extract text from resume for candidate {candidate_id}")
            return
        
        # Step 2: Analyze resume with Gemini for scoring
        logger.info(f"Analyzing resume for candidate {candidate_id}")
        scores = gemini_service.analyze_resume(
            resume_text=resume_text,
            job_description=job.job_description,
            expected_skills=job.expected_skills
        )
        
        # Step 3: Update candidate scores
        candidate.skills_match_score = scores["skills_match_score"]
        candidate.resume_relevancy_score = scores["resume_relevancy_score"]
        candidate.job_description_relevancy_score = scores["job_description_relevancy_score"]
        
        logger.info(f"Scores for candidate {candidate_id}: "
                   f"Skills: {scores['skills_match_score']}, "
                   f"Relevancy: {scores['resume_relevancy_score']}, "
                   f"JD Match: {scores['job_description_relevancy_score']}")
        
        # Step 4: Generate interview Q&A
        logger.info(f"Generating interview questions for candidate {candidate_id}")
        qa_data = gemini_service.generate_interview_questions(
            resume_text=resume_text,
            job_description=job.job_description,
            expected_skills=job.expected_skills
        )
        
        # Step 5: Create PDF document
        if qa_data and any(qa_data.get(f'interview_{i}', []) for i in range(1, 4)):
            logger.info(f"Creating Q&A PDF for candidate {candidate_id}")
            pdf_data = gemini_service.create_qa_pdf(
                qa_data=qa_data,
                candidate_name=candidate.name
            )
            
            # Step 6: Save PDF to database
            candidate.qa_document_data = pdf_data
            candidate.qa_document_filename = f"interview_guide_{candidate.name.replace(' ', '_')}_{candidate.id}.pdf"
            logger.info(f"Q&A PDF created successfully for candidate {candidate_id}")
        else:
            logger.warning(f"No Q&A data generated for candidate {candidate_id}")
        
        # Commit all changes
        db.commit()
        logger.info(f"Resume scanning completed successfully for candidate {candidate_id}")
        
    except Exception as e:
        logger.error(f"Error in scan_resume_background for candidate {candidate_id}: {str(e)}")
        db.rollback()

