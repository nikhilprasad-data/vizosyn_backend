from fastapi import APIRouter, status, HTTPException, Depends
from src.schemas import TeamBase, TeamResponse,TeamUpdate, TeamViewTeamMember, TeamViewTeamMemberResponse
from sqlalchemy.orm import Session
from src.config.settings import get_db
from src.services import get_id
from src.models import User, Profile, Team, TeamMember,TeamRequest
from sqlalchemy.sql import func

team = APIRouter()

@team.post('/create-team',response_model= TeamResponse ,status_code= status.HTTP_201_CREATED)
def create_team(new_team: TeamBase, db: Session= Depends(get_db), admin_id: int= Depends(get_id)):
     """Initializes a new team and automatically assigns the creator as the admin and first member."""

     existing_user = db.query(User).filter(User.id == admin_id, User.is_active == True).first()

     if not existing_user:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "User not found."
          )
     
     existing_profile = db.query(Profile).filter(Profile.user_id == admin_id, Profile.is_active == True).first()

     if not existing_profile:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Profile not found or has been deleted. Please create a new profile."
          )
     
     existing_team = db.query(TeamMember).filter(TeamMember.user_id == admin_id, TeamMember.is_active == True).first()

     if existing_team:
          raise HTTPException(
               status_code    = status.HTTP_400_BAD_REQUEST,
               detail         = "You are already a member of a team. You cannot create a new one."
          )
     
     add_team = Team(
          name           = new_team.name.strip().title(),
          description    = new_team.description,
          admin_id       = admin_id,
     )
     try:
          db.add(add_team)
          db.flush()

          add_team_member = TeamMember(
               team_id = add_team.id,
               user_id = admin_id
          )

          db.add(add_team_member)
          db.commit()
          db.refresh(add_team_member)

          team_data = {
               "name"              : add_team.name,
               "description"       : add_team.description,
               "id"                : add_team.id,
               "admin_id"          : admin_id,
               "admin_username"    : existing_user.username,
          }

          return team_data

     except Exception as e:
          db.rollback()
          print(e)

          if "unique constraint" in str(e).lower() and "teams_name" in str(e).lower():
               raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail = "A team with this name already exists. Please choose a different name."
               )
                 
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error"
          )

@team.get('/view-my-team', response_model= TeamResponse, status_code= status.HTTP_200_OK)
def get_my_team(id: int= Depends(get_id), db: Session= Depends(get_db)):
     """Retrieves detailed information and current status of the team the authenticated user belongs to."""

     existing_user = db.query(User).filter(User.id == id, User.is_active == True).first()

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
     
     existing_team_member = db.query(TeamMember).filter(TeamMember.user_id == id, TeamMember.is_active == True).first()

     if not existing_team_member:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Team not found. Please join or create a new  team."
          )
     
     existing_team_details = db.query(Team).filter(Team.id == existing_team_member.team_id, Team.is_active  == True).first()

     if not existing_team_details:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Team details not found or have been deleted."
          )

     try:

          admin_username = db.query(User.username).filter(User.id == existing_team_details.admin_id, User.is_active == True).scalar()

          current_members_count = db.query(TeamMember).filter(TeamMember.team_id == existing_team_details.id, TeamMember.is_active == True).count()

          if current_members_count < int(existing_team_details.max_members):
               team_status = "Open"

          else:
               team_status = "Full"
     
          team_details = {
                         "name"                   : existing_team_details.name,
                         "description"            : existing_team_details.description,
                         "id"                     : existing_team_details.id,
                         "admin_id"               : existing_team_details.admin_id,
                         "admin_username"         : admin_username,
                         "status"                 : team_status,
                         "current_members_count"  : current_members_count,
                         "created_at"             : existing_team_details.created_at,
                         "is_active"              : existing_team_details.is_active
                    }

          return team_details
     
     except Exception as e:
          print(e)
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error while fetching team details."
          )

@team.get('/view-all-team', response_model= list[TeamResponse], status_code= status.HTTP_200_OK)
def get_all_team(id: int= Depends(get_id),db: Session= Depends(get_db)):
     """Returns a comprehensive, aggregated list of all active teams on the platform."""
     
     existing_user = db.query(User).filter(User.id == id).first()

     if not existing_user:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "User not found."
          )
     
     try:

          all_team_list = []

          team_query     = db.query(Team, 
                                   User.username.label("admin_username"),
                                   func.count(TeamMember.id).label("current_members_count")
                                   ).join(User, Team.admin_id == User.id
                                   ).outerjoin(TeamMember, Team.id == TeamMember.team_id
                                   ).filter(Team.is_active == True
                                   ).group_by(Team.id,User.username
                                   ).order_by(Team.created_at.desc()
                                   ).all()

          for team, admin_username, current_members_count in team_query:

               if current_members_count < team.max_members:
                    team_status = "Open"
               else:
                    team_status = "Full"

               all_team_dict = {
                    "name"                   : team.name,
                    "description"            : team.description,
                    "id"                     : team.id,
                    "admin_id"               : team.admin_id,
                    "admin_username"         : admin_username,
                    "status"                 : team_status,
                    "current_members_count"  : current_members_count,
                    "created_at"             : team.created_at,
                    "is_active"              : team.is_active
               }

               all_team_list.append(all_team_dict)
          
          return all_team_list
     
     except Exception as e:
          print(e)
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error while fetching teams."
          )

@team.delete('/delete-my-team', status_code= status.HTTP_200_OK)
def delete_my_team(id: int= Depends(get_id), db: Session= Depends(get_db)):
     """Soft-deletes the team and removes all active member associations (Admin only)."""

     existing_user = db.query(User).filter(User.id == id, User.is_active == True).first()

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
     
     existing_team_member = db.query(TeamMember).filter(TeamMember.user_id == id,TeamMember.is_active == True).first()

     if not existing_team_member:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "You are not part of any team, so there is no team to delete."
          )

     existing_team_details = db.query(Team).filter(Team.id == existing_team_member.team_id, Team.is_active  == True).first()

     if not existing_team_details:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Team details not found or have been deleted already."
          )
     
     if id != existing_team_details.admin_id:
          raise HTTPException(
               status_code    = status.HTTP_403_FORBIDDEN,
               detail         = "Access Denied. Only the team admin has the rights to delete the team."
          )
     
     try:
          db.query(Team).filter(Team.id == existing_team_details.id).update({"is_active" : False})
          db.query(TeamMember).filter(TeamMember.team_id == existing_team_details.id).delete() 
          db.commit()

          return {"message": "Successfully deleted the team and freed all members."}
     
     except Exception as e:
          db.rollback()
          print(e)
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error while deleting the team."
          )

@team.patch('/update-my-team', status_code= status.HTTP_200_OK)
def update_my_team(update_team: TeamUpdate,id: int= Depends(get_id),db: Session= Depends(get_db)):
     """Applies partial updates to the team's existing properties (Admin only)."""

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
     
     existing_team_member = db.query(TeamMember).filter(TeamMember.user_id == id, TeamMember.is_active == True).first()

     if not existing_team_member:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "You are not part of any team, so there is no team to update."
          )

     existing_team_details = db.query(Team).filter(Team.id == existing_team_member.team_id, Team.is_active  == True).first()

     if not existing_team_details:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Team details not found or have been deleted already."
          )
     
     if id != existing_team_details.admin_id:
          raise HTTPException(
               status_code    = status.HTTP_403_FORBIDDEN,
               detail         = "Access Denied. Only the team admin has the rights to update the team."
          )
     
     try:
          update_fields = update_team.model_dump(exclude_unset= True)

          if "name" in update_fields and update_fields["name"]:
               update_fields["name"] = update_fields["name"].strip().title()

          for key, value in update_fields.items():
               setattr(existing_team_details, key, value)
          db.commit()

          return {"message": "Successfully updated the team."}
     
     except Exception as e:
          db.rollback()
          print(e)

          if "unique constraint" in str(e).lower() and "teams_name" in str(e).lower():
               raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail = "A team with this name already exists. Please choose a different name."
               )
          
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error while updating the team."
          )

@team.put('/replace-my-team', status_code= status.HTTP_200_OK)
def replace_my_team(replace_team: TeamBase,id: int= Depends(get_id),db: Session= Depends(get_db)):
     """Completely overwrites the team's core information with a new dataset (Admin only)."""

     existing_user = db.query(User).filter(User.id == id, User.is_active == True).first()

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
     
     existing_team_member = db.query(TeamMember).filter(TeamMember.user_id == id, TeamMember.is_active == True).first()

     if not existing_team_member:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "You are not part of any team, so there is no team to replace."
          )

     existing_team_details = db.query(Team).filter(Team.id == existing_team_member.team_id, Team.is_active  == True).first()

     if not existing_team_details:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Team details not found or have been deleted already."
          )
     
     if id != existing_team_details.admin_id:
          raise HTTPException(
               status_code    = status.HTTP_403_FORBIDDEN,
               detail         = "Access Denied. Only the team admin has the rights to replace the team."
          )
     
     try:
          db.query(Team).filter(Team.id == existing_team_details.id).update({"name" : replace_team.name.strip().title(), 
                                                                             "description" : replace_team.description})
          db.commit()
          return {"message": "Successfully replaced the team."}
     
     except Exception as e:
          db.rollback()
          print(e)

          if "unique constraint" in str(e).lower() and "teams_name" in str(e).lower():
               raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail = "A team with this name already exists. Please choose a different name."
               )

          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error while replacing the team."
          )

@team.get('/view-my-team-members/{target_team_id}', response_model= list[TeamViewTeamMemberResponse], status_code= status.HTTP_200_OK)
def team_member(target_team_id: int, id: int= Depends(get_id), db: Session= Depends(get_db)):
     """
     Retrieves profile details of all members within the specified team.
     Ensures the requesting user is active, holds a valid profile, and belongs to the target team.
     """
     
     existing_user = db.query(User).filter(User.id == id, User.is_active == True).first()

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

     existing_team_member = db.query(TeamMember).filter(TeamMember.user_id == id, TeamMember.is_active == True).first()

     if not existing_team_member:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "No active team association found for this account."
          )
     
     if not (target_team_id == existing_team_member.team_id):
          raise HTTPException(
               status_code    = status.HTTP_403_FORBIDDEN,
               detail         = "Access Denied: You do not have permission to view members of other teams."
          )
     
     try:
          all_team_member          = db.query(TeamMember).filter(TeamMember.team_id == existing_team_member.team_id, TeamMember.is_active == True).all()

          all_team_member_id       = [member.user_id for member in all_team_member]

          all_team_member_lst      = []

          all_team_member_profile  = db.query(Profile).filter(Profile.user_id.in_(all_team_member_id)).all()

          for member in all_team_member_profile:
               all_team_member_dict = {
                    "team_member_name"            : member.full_name,
                    "team_member_github_url"      : member.github_url,
                    "team_member_linkedin_url"    : member.linkedin_url,
                    "team_member_user_id"         : member.user_id
               }
               all_team_member_lst.append(all_team_member_dict)
          
          return all_team_member_lst
     
     except Exception as e:
          print(e)
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error: Unable to process the request for team data."
          )