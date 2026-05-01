from pydantic import BaseModel, Field, ConfigDict
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