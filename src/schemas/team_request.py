from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from typing import Optional
from datetime import datetime

class TeamRequestBase(BaseModel):

     """Schema for capturing a user's request to join a specific team."""

     team_id : int 

     team_name: str

     message: Optional[str] = Field(default= None,max_length= 100, description="Custom cover message addressed to the team admin")

class TeamRequestResponse(BaseModel):

     """Schema for displaying team request details alongside applicant metrics."""

     id: int

     team_id: int

     user_id:int

     status: Optional[str] = "Pending"

     message: str

     requested_at: Optional[datetime] = datetime.utcnow()

     full_name: str

     bio: str

     github_url: HttpUrl

     linkedin_url: HttpUrl

     city: str 

     state: str

     model_config = ConfigDict(from_attributes= True)

class TeamRequestHandle(BaseModel):

     """Schema for admins to process (Accept/Reject) pending team join requests."""

     request_id : int

     action: str