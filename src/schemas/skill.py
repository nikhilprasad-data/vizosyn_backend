from pydantic import BaseModel, ConfigDict

class SkillUser(BaseModel):
     """Schema to validate a list of skills received from the frontend search payload."""
     
     skill_names: list[str]

class SkillUserResponse(BaseModel):
     """Schema representing a user's name and unique ID for frontend routing."""

     full_name: str

     user_id: int

     model_config = ConfigDict(from_attributes = True)