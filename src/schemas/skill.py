from pydantic import BaseModel

class Skill(BaseModel):
     """Schema to validate a list of skills received from the frontend search payload."""
     
     skill_names: list[str]
