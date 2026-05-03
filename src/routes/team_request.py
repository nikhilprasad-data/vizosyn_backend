from fastapi import APIRouter, status, HTTPException, Depends
from src.schemas import TeamRequestBase, TeamRequestResponse, TeamRequestHandle
from sqlalchemy.orm import Session
from src.config.settings import get_db
from src.services import get_id
from src.models import User, Location, Profile, TeamMember, Team, TeamRequest

team_request = APIRouter()

@team_request.post('/send-request', response_model=TeamRequestResponse, status_code= status.HTTP_200_OK)
def send_request(new_team_request: TeamRequestBase,id: int= Depends(get_id), db: Session= Depends(get_db)):
     """Submits a new team join request for the authenticated user."""

     existing_user= db.query(User).filter(User.id == id, User.is_active == True).first()
     if not existing_user:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "User Not Found"
          )

     existing_profile= db.query(Profile).filter(Profile.user_id == id, Profile.is_active == True).first()
     if not existing_profile:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Profile not found or has been deleted. Please create a new profile.To Join Team"
          )

     existing_team_member= db.query(TeamMember).filter(TeamMember.user_id == id, TeamMember.is_active == True).first()
     if existing_team_member:
          raise HTTPException(
               status_code    = status.HTTP_400_BAD_REQUEST,
               detail         = "You are already part of a team."
          )
     
     existing_team= db.query(Team).filter(Team.id == new_team_request.team_id, Team.name == new_team_request.team_name, Team.is_active == True).first()
     if not existing_team:
          raise HTTPException(
               status_code    = status.HTTP_400_BAD_REQUEST,
               detail         = "Team not Found or has been deleted."
          )
     
     if existing_team.status == "Full": #type: ignore
          raise HTTPException(
               status_code    = status.HTTP_400_BAD_REQUEST,
               detail         = "This team is currently full and cannot accept new members."
          )
     
     existing_request= db.query(TeamRequest).filter(TeamRequest.user_id == id, TeamRequest.team_id == existing_team.id ,TeamRequest.status == "Pending").first()
     if existing_request:
          raise HTTPException(
               status_code    = status.HTTP_400_BAD_REQUEST,
               detail         = "Request already sent."
          )
     try:
          new_request = TeamRequest(
               team_id   = existing_team.id,
               user_id   = id,
               status    = "Pending",
               message   = new_team_request.message,
          )

          db.add(new_request)
          db.commit()
          db.refresh(new_request)

          show_request = {
               "id"           : new_request.id,
               "team_id"      : new_request.team_id,
               "user_id"      : new_request.user_id,
               "status"       : new_request.status,
               "message"      : new_request.message,
               "full_name"    : existing_profile.full_name,
               "bio"          : existing_profile.bio,
               "github_url"   : existing_profile.github_url,
               "linkedin_url" : existing_profile.linkedin_url,
               "city"         : db.query(Location.city).filter(Location.id == existing_profile.location_id).scalar(), 
               "state"        : db.query(Location.state).filter(Location.id == existing_profile.location_id).scalar(),
          }

          return show_request
     
     except Exception as e:
          db.rollback()
          print(e)
          raise HTTPException(
               status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail= "Internal Server Error while sending the request."
          )

@team_request.get('/view-request', response_model= list[TeamRequestResponse], status_code= status.HTTP_200_OK)
def view_request(admin_id: int= Depends(get_id), db: Session= Depends(get_db)):
     """Retrieves a list of pending team join requests for the admin's team."""

     existing_user= db.query(User).filter(User.id == admin_id, User.is_active == True).first()
     if not existing_user:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "User Not Found"
          )

     existing_profile= db.query(Profile).filter(Profile.user_id == admin_id, Profile.is_active == True).first()
     if not existing_profile:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Profile not found or deactivated."
          )
          
     existing_team= db.query(Team).filter(Team.admin_id == admin_id).first()
     if not existing_team:
          raise HTTPException(
               status_code    = status.HTTP_403_FORBIDDEN,
               detail         = "Access Denied. Only active team admins can view team requests."
          )
     
     try:

          all_request_lst = []

          team_request_query = db.query(
                                        TeamRequest.id.label("id"),
                                        TeamRequest.team_id.label("team_id"),
                                        User.id.label("user_id"),
                                        TeamRequest.status.label("status"),
                                        TeamRequest.message.label("message"),
                                        Profile.full_name.label("full_name"),
                                        Profile.bio.label("bio"),
                                        Profile.github_url.label("github_url"),
                                        Profile.linkedin_url.label("linkedin_url"),
                                        Location.city.label("city"),
                                        Location.state.label("state")
                                        ).join(TeamRequest, User.id == TeamRequest.user_id
                                        ).join(Profile, User.id == Profile.user_id
                                        ).join(Location, Profile.location_id == Location.id
                                        ).filter(TeamRequest.team_id == existing_team.id, TeamRequest.status == "Pending"
                                        ).all()
          
          for request_info in  team_request_query:
               all_request_lst.append(request_info)
          

          return all_request_lst
     
     except Exception as e:
          print(e)
          raise HTTPException(
               status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail= "Internal Server Error. While fetching team request."
          )
     
@team_request.patch('/process-request', status_code= status.HTTP_200_OK)
def process_request(request_handle: TeamRequestHandle,admin_id: int= Depends(get_id), db: Session= Depends(get_db)):
     """Processes a pending team join request by allowing the team admin to accept or reject it."""

     existing_user   = db.query(User).filter(User.id == admin_id, User.is_active == True).first()
     if not existing_user:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "User not found"
          )

     existing_profile    = db.query(Profile).filter(Profile.user_id == admin_id, Profile.is_active == True).first()
     if not existing_profile:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Profile not found or deactivated."
          )
     
     existing_team  = db.query(Team).filter(Team.admin_id == admin_id, Team.is_active == True).first()
     if not existing_team:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Access Denied. Only active team admins can handle requests."
          )
     
     target_request = db.query(TeamRequest).filter(TeamRequest.id == request_handle.request_id, 
                                            TeamRequest.team_id == existing_team.id, 
                                            TeamRequest.status =="Pending").first()
     if not target_request:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Pending Team Request not found."
               )

     if request_handle.action == "Rejected":
          try:
               target_request.status = "Rejected" # type: ignore
               db.commit()
               return {"message" : "Successfully Rejected Request."}

          except Exception as e:
               db.rollback()
               print(e)
               raise HTTPException(
                    status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail         = "Internal Server Error while rejecting request."
               )
          
     elif request_handle.action == "Accepted":

          if existing_team.status == "Full":#type: ignore
               raise HTTPException(
                    status_code    = status.HTTP_400_BAD_REQUEST,
                    detail         = "Team has reached its maximum member limit."
                    )

          count_total_member = db.query(TeamMember).filter(TeamMember.team_id == existing_team.id, 
                                                           TeamMember.is_active == True).count()

          if count_total_member >= existing_team.max_members:#type: ignore
               raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Team has reached its maximum member limit."
                    )
          
          existing_requesting_user_team = db.query(TeamMember).filter(TeamMember.user_id == target_request.user_id, 
                                                                      TeamMember.is_active == True).first() # type: ignore

          if existing_requesting_user_team:
               raise HTTPException(
                    status_code    = status.HTTP_400_BAD_REQUEST, 
                    detail         = "User is already active in another team."
                    )
          
          try:
               target_request.status = "Accepted"      #type: ignore

               new_team_member = TeamMember(
                    team_id   = existing_team.id,
                    user_id   = target_request.user_id        #type: ignore
               )
               db.add(new_team_member)
               db.flush()

               new_count_team_members = db.query(TeamMember).filter(TeamMember.team_id == existing_team.id, 
                                                                    TeamMember.is_active == True).count()

               if new_count_team_members >= existing_team.max_members:      #type: ignore
                    existing_team.status = "Full"                           #type: ignore
               
               db.commit()

               return {"message" : "Successfully Added to the team."}
          
          except Exception as e:
               db.rollback()
               print(e)
               raise HTTPException(
                    status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR, 
                    detail         = "Internal Server Error while adding user to team."
                    )
     else:
          raise HTTPException(
               status_code    = status.HTTP_400_BAD_REQUEST, 
               detail         = "Invalid Action provided."
               )