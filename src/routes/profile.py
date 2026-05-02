from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from src.schemas import ProfileBase, ProfileResponse, ProfileUpdate
from src.config.settings import get_db
from src.services import get_id, get_location_id
from src.models import User, Profile, Location

profile = APIRouter()

@profile.post('/create-profile', response_model= ProfileResponse, status_code= status.HTTP_201_CREATED)
def create_profile(new_profile: ProfileBase, db: Session= Depends(get_db), id: int= Depends(get_id)):
     """Creates a new user profile and maps it to a geographic location."""

     existing_user = db.query(User).filter(User.id == id).first()

     if not existing_user:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Invalid Credentials"
          )
     
     existing_profile = db.query(Profile).filter(Profile.user_id == id).first()

     if existing_profile:
          raise HTTPException(
               status_code    = status.HTTP_400_BAD_REQUEST,
               detail         = "Profile Already Exists"
          )
     
     user_location = {"city" : new_profile.city.strip().title(), "state" : new_profile.state.strip().title()}

     location_id = get_location_id(user_location= user_location, db= db)

     add_profile    = Profile(
          user_id        = id,
          location_id    = location_id,
          full_name      = new_profile.full_name,
          bio            = new_profile.bio,
          github_url     = new_profile.github_url,
          linkedin_url   = new_profile.linkedin_url ,
     )

     try:
          db.add(add_profile)
          db.commit()
          db.refresh(add_profile)

          return add_profile
     
     except Exception as e:
          db.rollback()
          print(e)
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error"
          )

@profile.get('/view-my-profile', response_model= ProfileResponse ,status_code= status.HTTP_200_OK)
def get_profile(id: int= Depends(get_id), db:Session= Depends(get_db)):
     """Fetches the authenticated user's active profile and location details."""

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
     
     existing_location = db.query(Location).filter(Location.id == existing_profile.location_id).first()

     profile_data = {
          "id"           : existing_profile.id,
          "user_id"      : id,
          "location_id"  : existing_profile.location_id,
          "full_name"    : existing_profile.full_name,
          "bio"          : existing_profile.bio,
          "github_url"   : existing_profile.github_url,
          "linkedin_url" : existing_profile.linkedin_url,
          "is_active"    : existing_profile.is_active,
          "city"         : existing_location.city if existing_location else "",
          "state"        : existing_location.state if existing_location else ""
     }

     return profile_data

@profile.delete('/delete-my-profile', status_code= status.HTTP_200_OK)
def delete_profile(id: int= Depends(get_id), db: Session= Depends(get_db)):
     """Soft-deletes the user's profile by setting the active status to false."""

     existing_user = db.query(User).filter(User.id == id).first()

     if not existing_user:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "User not found."
          )

     existing_profile = db.query(Profile).filter(Profile.user_id == id).first()

     if not existing_profile:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "Profile not found. Please create a profile first."
          )
     
     db.query(Profile).filter(Profile.user_id == id).update({"is_active" : False})   
     db.commit()     

     return {"message" : "Successfully Deleted Profile"}

@profile.put('/replace-my-profile', response_model= ProfileResponse ,status_code= status.HTTP_200_OK)
def replace_profile(replace_profile: ProfileBase, id: int= Depends(get_id), db: Session= Depends(get_db)):
     """Completely overwrites an existing user profile with a new dataset."""

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
     
     user_location = {"city" : replace_profile.city.strip().title(), "state" : replace_profile.state.strip().title()}

     location_id = get_location_id(user_location= user_location, db= db)

     try:

          db.query(Profile).filter(Profile.user_id == id).update({
               "location_id"  : location_id,
               "full_name"    : replace_profile.full_name.strip().title(),    
               "bio"          : replace_profile.bio,
               "github_url"   : replace_profile.github_url,
               "linkedin_url" : replace_profile.linkedin_url
          })
          db.commit()
          db.refresh(existing_profile)

          replaced_profile_data = {
          "id"           : existing_profile.id,
          "user_id"      : id,
          "location_id"  : location_id,
          "full_name"    : replace_profile.full_name.strip().title(),
          "bio"          : replace_profile.bio,
          "github_url"   : replace_profile.github_url,
          "linkedin_url" : replace_profile.linkedin_url,
          "city"         : replace_profile.city.strip().title(),
          "state"        : replace_profile.state.strip().title()
          }

          return replaced_profile_data
     
     except Exception as e:
          db.rollback()
          print(e)
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error"
          )

@profile.patch('/update-my-profile', response_model= ProfileResponse, status_code= status.HTTP_200_OK)
def update_profile(update_profile: ProfileUpdate, db: Session= Depends(get_db), id: int= Depends(get_id)):
     """Partially updates specific fields within the user's existing profile."""

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
     
     final_location_id = existing_profile.location_id

     if (update_profile.city and update_profile.state):
          user_location = {"city" : update_profile.city.strip().title(), 
                         "state" : update_profile.state.strip().title()}
          
          final_location_id = get_location_id(user_location= user_location, db= db)
     
     update_data = update_profile.model_dump(exclude_unset= True)

     update_data.pop("city", None)
     update_data.pop("state", None)

     try:
          if "full_name" in update_data and update_data["full_name"]:
               update_data["full_name"] = update_data["full_name"].strip().title()

          for key, value in update_data.items():
               setattr(existing_profile, key, value)
          
          existing_profile.location_id = final_location_id
          
          db.commit()
          db.refresh(existing_profile)

          existing_location = db.query(Location).filter(Location.id == final_location_id).first()
          
          updated_profile_data = {
               "id"           : existing_profile.id,
               "user_id"      : id,
               "location_id"  : final_location_id,
               "full_name"    : existing_profile.full_name,
               "bio"          : existing_profile.bio,
               "github_url"   : existing_profile.github_url,
               "linkedin_url" : existing_profile.linkedin_url,
               "city"         : existing_location.city if existing_location else "",
               "state"        : existing_location.state if existing_location else ""
               }

          return updated_profile_data
     
     except Exception as e:
          db.rollback()
          print(e)
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error"
          )

@profile.get('/view-all-profile', response_model= list[ProfileResponse], status_code= status.HTTP_200_OK)
def view_all_profile(id: int= Depends(get_id), db: Session= Depends(get_db)):
     """Retrieves a comprehensive directory of all active user profiles."""
     
     existing_user = db.query(User).filter(User.id == id, User.is_active == True).first()
     if not existing_user:
          raise HTTPException(
               status_code    = status.HTTP_404_NOT_FOUND,
               detail         = "User not found."
          )
     
     try:
               
          all_profile = db.query(Profile).filter(Profile.is_active == True).all()

          all_profile_lst = []

          for profile in all_profile:

               profile_dict = {
                    "full_name"    : profile.full_name,
                    "bio"          : profile.bio,
                    "github_url"   : profile.github_url,
                    "linkedin_url" : profile.linkedin_url,
                    "city"         : db.query(Location.city).filter(Location.id == profile.location_id).scalar(),
                    "state"        : db.query(Location.state).filter(Location.id == profile.location_id).scalar(),
                    "id"           : profile.id,
                    "user_id"      : profile.user_id,
                    "location_id"  : profile.location_id,
                    "is_active"    : profile.is_active,
                    
               }

               all_profile_lst.append(profile_dict)
          
          return all_profile_lst
     
     except Exception as e:
          print(e)
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error"
          )