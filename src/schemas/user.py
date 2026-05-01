from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):

     """Core user attributes shared across multiple schemas."""
     
     username: str

     email: EmailStr

class UserSignup(UserBase):

     """Schema for validating new user registration payloads."""

     password: str

class UserLogin(BaseModel):

     """Schema for authenticating user login requests."""

     email: EmailStr

     password: str

class UserResponse(UserBase):

     """Schema for safely serializing user data in API responses."""
     
     id: int

     is_active: Optional[bool] = True

     created_at: Optional[datetime] = datetime.utcnow()

     model_config   = ConfigDict(from_attributes= True)