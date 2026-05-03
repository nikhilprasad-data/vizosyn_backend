from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from src.schemas import UserSkillViewResponse
from src.services import get_id
from src.config.settings import get_db
from src.models import User, UserSkill, Skill


user_skill = APIRouter()

@user_skill.get('/view-user-skill/{target_user_id}', response_model= UserSkillViewResponse, status_code= status.HTTP_200_OK)
def view_user_skill(target_user_id: int, id : int= Depends(get_id), db: Session= Depends(get_db)):
     """Retrieves the list of skills for a specified target user."""
     
     existing_user = db.query(User).filter(User.id == id, User.is_active == True)
     if not existing_user:
          raise HTTPException(
               status_code    = status.HTTP_404,
               detail         = "User Not Found"
          )
     
     try:
     
          user_skill_info     = db.query(UserSkill).filter(UserSkill.user_id == target_user_id).all()

          user_skill_id       = [skill.skill_id for skill in user_skill_info]

          user_skill_name_info= db.query(Skill).filter(Skill.id.in_(user_skill_id)).all()

          user_skill_name     = [skill.skill_name for skill in user_skill_name_info]

          return {"skill_name" : user_skill_name if user_skill_name else ["No Skills Yet"]} 
     
     except Exception as e:
          print(e)
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error while fetching skills."
          )