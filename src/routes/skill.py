from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from src.models import Skill, UserSkill, User, Profile, Team, TeamMember
from src.schemas import UserSkillBase, UserSkillResponse
from src.config.settings import get_db 
from src.services import  get_id, skill_to_add

skill = APIRouter()

@skill.post('/add-skills', status_code= status.HTTP_200_OK)
def add_skill(skill: list[str], id: int= Depends(get_id), db: Session= Depends(get_db)):
     """Assigns a list of new skills to the authenticated user."""

     existing_user = db.query(User).filter(User.id == id).first()

     if not existing_user:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "User not found."
          )
     
     existing_profile = db.query(Profile).filter(Profile.user_id == id, Profile.is_active == True).first()

     if not existing_profile:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Profile not found or has been deleted. Please create a new profile."
          )

     try:
          user_skill_add = []

          skill_id_lst        = skill_to_add(db= db, skill_name_lst= skill)

          existing_user_skill = db.query(UserSkill).filter(UserSkill.user_id == id).all()

          user_skill_id       = [user_skill.skill_id for user_skill in existing_user_skill]

          for skill_id in skill_id_lst:

               if skill_id not in user_skill_id:
                    user_skill_add.append(UserSkill(user_id= id, skill_id= skill_id))

          if user_skill_add:
               db.add_all(user_skill_add)
               db.commit()

          return {"message": "Skills successfully updated."}
     
     except Exception as e:
          db.rollback()
          print(e)
          raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error while verifying skills."
          )

@skill.get('/view-my-skills', response_model= UserSkillResponse, status_code= status.HTTP_200_OK)
def show_skill(id: int= Depends(get_id), db: Session= Depends(get_db)):
     """Retrieves the current skillset and team status of the user."""

     existing_user = db.query(User).filter(User.id == id).first()

     if not existing_user:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "User not found."
          )
     
     existing_profile = db.query(Profile).filter(Profile.user_id == id, Profile.is_active == True).first()

     if not existing_profile:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Profile not found or has been deleted. Please create a new profile."
          )
     
     existing_user_skill = db.query(UserSkill).filter(UserSkill.user_id == id).all()

     if not existing_user_skill:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Skill not found or has been deleted. Please add skills."
          )

     try:
          user_name           = existing_user.username

          profile_id          = existing_profile.id

          team_id             = db.query(TeamMember.team_id).filter(TeamMember.user_id == id).scalar()

          team_name           = db.query(Team.name).filter(Team.id == team_id).scalar() or "Not In Team Yet"

          skill_id            = [record.skill_id for record in existing_user_skill]

          existing_skill      = db.query(Skill).filter(Skill.id.in_(skill_id)).all()

          existing_skill_name = [skill_name.skill_name for skill_name in existing_skill]

          skill_details = {
               "user_id"      : id,
               "user_name"    : user_name,
               "profile_id"   : profile_id,
               "team_name"    : team_name,
               "skill_name"   : existing_skill_name
          }

          return skill_details
     
     except Exception as e:
          print(e)
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error while fetching details."
          )

@skill.delete('/remove-skills', status_code= status.HTTP_200_OK)
def delete_skill(skill_to_delete: UserSkillBase, id: int= Depends(get_id), db: Session= Depends(get_db)):
     """Removes specified skills from the user's profile."""
     
     existing_user = db.query(User).filter(User.id == id).first()

     if not existing_user:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "User not found."
          )
     
     existing_profile = db.query(Profile).filter(Profile.user_id == id, Profile.is_active == True).first()

     if not existing_profile:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Profile not found or has been deleted. Please create a new profile."
          )
     
     existing_user_skill = db.query(UserSkill).filter(UserSkill.user_id == id).all()

     if not existing_user_skill:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Skill not found or has been deleted. Please add skills."
          )
     
     try:
          clean_skill_to_delete    = [s.strip().title() for s in skill_to_delete.skill_name]

          existing_skill           = db.query(Skill).filter(Skill.skill_name.in_(clean_skill_to_delete)).all()

          to_delete_skill_id        = [record.id for record in existing_skill]

          db.query(UserSkill).filter(UserSkill.skill_id.in_(to_delete_skill_id), UserSkill.user_id == id).delete(synchronize_session= False)

          db.commit()

          return {"message" : "Successfully removed skills"}
     
     except Exception as e:
          db.rollback()
          print(e)
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error while deleting."
          )