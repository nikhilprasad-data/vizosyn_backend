from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from src.schemas import UserSkillViewResponse, SkillUser, SkillUserResponse
from src.services import get_id
from src.config.settings import get_db
from src.models import User, UserSkill, Skill, Profile


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

@user_skill.post('/view-skill-user', response_model= list[SkillUserResponse], status_code= status.HTTP_200_OK)
def view_skill_user(skill_list: SkillUser, id: int=  Depends(get_id), db: Session= Depends(get_db)):
     """Fetches a detailed list of active users who possess the exact skills provided in the search payload."""
     
     existing_user = db.query(User).filter(User.id == id, User.is_active == True).first()

     if not existing_user:
          raise HTTPException(
               status_code    = status.HTTP_401_UNAUTHORIZED,
               detail         = "User not found"
          )
     
     try: 

          skill_info     = db.query(Skill).filter(Skill.skill_name.in_(skill_list.skill_names)).all()

          skill_id       = [ skill.id for skill in skill_info]

          existing_skilled_user_info = db.query(UserSkill).filter(UserSkill.skill_id.in_(skill_id)).all()

          skilled_user_id     = [ user.user_id for user in existing_skilled_user_info ]
          skilled_user_list   = []

          join_query =   db.query(UserSkill.user_id.label("user_id"), Profile.full_name.label("full_name") 
                         ).join(Profile, Profile.user_id == UserSkill.user_id
                         ).filter(UserSkill.user_id.in_(skilled_user_id)
                         ).all()
          
          for info in join_query:
               skill_user_dict = {
                    "user_id"      : info.user_id,
                    "full_name"    : info.full_name
               }

               skilled_user_list.append(skill_user_dict)

          return skilled_user_list
      
     except Exception as e:
          print(e)

          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error while fetching users."
          )