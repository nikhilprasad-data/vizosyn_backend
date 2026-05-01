from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from typing import Optional

class ProfileBase(BaseModel):

     """Core profile attributes representing a user's professional identity."""

     full_name: str

     bio: Optional[str] = Field(default= None, max_length= 500, description= "Professional summary or bio of the user")

     github_url: Optional[HttpUrl] = None

     linkedin_url: Optional[HttpUrl] = None

     city: str

     state: str

class ProfileResponse(ProfileBase):

     """Schema for exposing user profile data along with database IDs."""

     id: int

     user_id: int

     location_id: int

     is_active: Optional[bool] = True

     model_config = ConfigDict(from_attributes= True)

class ProfileUpdate(BaseModel):

     """Schema for handling partial updates to a user's professional profile."""

     full_name: Optional[str] = None

     bio: Optional[str] = Field(default= None, max_length= 500)

     github_url: Optional[HttpUrl] = None

     linkedin_url: Optional[HttpUrl] = None

     city: Optional[str] = None

     state: Optional[str] = None

     is_active: Optional[bool] = True