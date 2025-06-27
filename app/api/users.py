from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import firebase_admin
from firebase_admin import auth
import logging

from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserSignup, UserSignupResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/signup", response_model=UserSignupResponse)
async def signup(
    user_data: UserSignup,
    db: Session = Depends(get_db)
):
    """
    Create a new user account with email and password.
    This endpoint creates a user in Firebase and stores the user in the database.
    """
    try:
        # Validate terms acceptance
        if not user_data.accept_terms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must accept the terms and conditions to create an account"
            )
        
        # Check if user already exists in database
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user in Firebase
        firebase_user = auth.create_user(
            email=user_data.email,
            password=user_data.password,
            email_verified=False
        )
        
        # Create user in database
        db_user = User(
            email=user_data.email,
            firebase_uid=firebase_user.uid,
            terms_accepted=True,
            terms_accepted_at=datetime.utcnow()
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Send email verification (optional)
        try:
            verification_link = auth.generate_email_verification_link(user_data.email)
            logger.info(f"Email verification link generated for {user_data.email}")
            # In production, you would send this link via email
        except Exception as e:
            logger.warning(f"Could not generate email verification link: {e}")
        
        return UserSignupResponse(
            message="User created successfully. Please verify your email.",
            email=user_data.email,
            firebase_uid=firebase_user.uid
        )
        
    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists in Firebase"
        )
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        # Clean up database if Firebase creation succeeded but DB failed
        if 'firebase_user' in locals():
            try:
                auth.delete_user(firebase_user.uid)
            except:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.post("/accept-terms", response_model=UserResponse)
async def accept_terms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.terms_accepted:
        raise HTTPException(status_code=400, detail="Terms already accepted")
    
    current_user.terms_accepted = True
    current_user.terms_accepted_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user