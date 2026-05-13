from pydantic import BaseModel

class Skill(BaseModel):
     """Schema to validate a list of skills received from the frontend search payload."""
     
     skill_names: list[str]

class SkillUser(BaseModel):
     """Schema representing a user's name and unique ID for frontend routing."""

     user: str

     user_id: int