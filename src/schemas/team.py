from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from typing import Optional
from datetime import datetime

class TeamBase(BaseModel):

     """Base schema for team creation and validation."""

     name: str = Field(max_length= 100, description="Unique registered name of the team")

     description: Optional[str] = Field(default= None, max_length= 500)

class TeamResponse(TeamBase):

     """Schema for returning complete team details to the client."""

     id: int

     admin_id: int

     admin_username: str

     max_members: Optional[int] = 5

     created_at: Optional[datetime] = datetime.utcnow()

     status: Optional[str] = "Open"

     current_members_count: Optional[int] = 1

     is_active: Optional[bool] = True

     model_config = ConfigDict(from_attributes= True)

class TeamUpdate(BaseModel):

     """Schema for processing partial updates (PATCH) to an existing team."""
     
     name: Optional[str] = Field(max_length= 100)

     description: Optional[str] = Field(default= None, max_length= 500)

class TeamViewTeamMember(BaseModel):
     """Schema for validating team identification."""

     team_id: int

class TeamViewTeamMemberResponse(BaseModel):
     """Schema for returning team member profile details in responses."""
     
     team_member_name: str

     team_member_github_url: HttpUrl

     team_member_linkedin_url: HttpUrl

     team_member_user_id: int

     model_config = ConfigDict(from_attributes= True)