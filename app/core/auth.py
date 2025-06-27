from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import firebase_admin
from firebase_admin import auth, credentials
import os
from pathlib import Path

from app.settings import settings
from app.db.session import get_db
from app.models.user import User
from app.core.firebase_helper import get_firebase_credentials_path


# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    try:
        # Try to get Firebase credentials path (handles base64 encoded creds in production)
        firebase_cred_path = get_firebase_credentials_path()
        
        if firebase_cred_path:
            cred = credentials.Certificate(firebase_cred_path)
            firebase_admin.initialize_app(cred)
        elif settings.FIREBASE_PROJECT_ID:
            # Initialize with project ID for development
            firebase_admin.initialize_app(options={
                'projectId': settings.FIREBASE_PROJECT_ID,
            })
        else:
            raise ValueError(
                "Firebase configuration missing. Please set either FIREBASE_CREDENTIALS_PATH, "
                "FIREBASE_CREDENTIALS_BASE64, or FIREBASE_PROJECT_ID in your environment variables."
            )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to initialize Firebase: {e}")
        raise


security = HTTPBearer()


async def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token_data: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
) -> User:
    firebase_uid = token_data.get("uid")
    email = token_data.get("email")
    
    if not firebase_uid or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token data"
        )
    
    # Check if user exists in database
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    
    if not user:
        # Create new user
        user = User(
            firebase_uid=firebase_uid,
            email=email
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.terms_accepted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Terms and conditions must be accepted"
        )
    return current_user