from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class UserSkillBase(BaseModel):

     """Schema for validating and adding technical or soft skills."""

     skill_name: list[str] = Field(description="List of skills associated with the user")

class UserSkillResponse(BaseModel):

     """Schema for returning aggregated user skills with profile context."""

     user_id: int

     user_name: str

     profile_id: int

     team_name: Optional[str] = Field(default= "Not In Team Yet")

     skill_name: list[str]

     model_config = ConfigDict(from_attributes= True)