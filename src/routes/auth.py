from fastapi import APIRouter, status, HTTPException, Depends
from src.config.settings import get_db
from src.schemas import UserSignup, UserResponse, UserLogin
from src.models import User
from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.services import generate_password_hash, check_password_hash, create_access_token,get_info


auth = APIRouter()

@auth.post('/signup', response_model= UserResponse, status_code= status.HTTP_201_CREATED)
def signup(new_user: UserSignup, db: Session= Depends(get_db)):
     """Registers a new user account with secure password hashing."""
          
     existing_user  = db.query(User).filter(or_(User.username == new_user.username,
                                                User.email == new_user.email)).first()

     if existing_user:
          raise HTTPException(
               status_code    = status.HTTP_400_BAD_REQUEST,
               detail         = "Username or Email already registered."
          )

     try:
          new_user_password_hash  = generate_password_hash(plain_password= new_user.password)

          add_user  = User(
               username       = new_user.username.strip().title(),
               email          = new_user.email.strip(),
               password_hash  = new_user_password_hash.strip()
          )

          db.add(add_user)
          db.commit()
          db.refresh(add_user)

          return add_user

     except Exception as e:
          db.rollback()
          print(e)
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         ="Internal Server Error."
          )

@auth.post('/login', status_code= status.HTTP_200_OK)
def login(user_credentials: UserLogin, db: Session= Depends(get_db)):
     """Authenticates user credentials and issues a JWT access token."""

     existing_user  = db.query(User).filter(User.email == user_credentials.email).first()

     plain_password = user_credentials.password

     if not (existing_user and check_password_hash(plain_password= plain_password, hash_password= str(existing_user.password_hash))):
          raise HTTPException(
               status_code= status.HTTP_401_UNAUTHORIZED,
               detail="Invalid Credentials"
          )
     try: 
          access_token   = create_access_token(identity= {"id" : existing_user.id, "username" : existing_user.username})

          return {
               "access_token" : access_token,
               "token_type"   : "bearer",
               "message"      : "success" 
          }
     
     except Exception as e:
          print(e)
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error."
          )

@auth.post('/logout', status_code= status.HTTP_200_OK)
def logout(identity: dict= Depends(get_info)):
     """Invalidates the current session (Requires client-side token removal)."""
     try:
          id        = identity.get("id")
          username  = identity.get("username")

          return {
               "status"  : "success",
               "message" : "Successfully Logged Out. Please remove the token from your client.",
               "user"    : username,
               "id"      : id
          }

     
     except Exception as e:
          print(e)
          raise HTTPException(
          status_code         = status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail              = "Internal Server Error"
          )