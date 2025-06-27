from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    firebase_uid: str


class UserSignup(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    accept_terms: bool = Field(..., description="User must accept terms and conditions")


class UserSignupResponse(BaseModel):
    message: str
    email: str
    firebase_uid: str


class UserUpdate(BaseModel):
    terms_accepted: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    firebase_uid: str
    terms_accepted: bool
    terms_accepted_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True