from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from src.config.database import Config
from typing import Optional
from src.models import Location

oauth2passwordbearer = OAuth2PasswordBearer(tokenUrl= '/auth/login')

SECRET_KEY=Config.SECRET_KEY
ALGORITHM=Config.ALGORITHM

def get_id(token: str= Depends(oauth2passwordbearer)):
     """Validates the JWT token and extracts the authenticated user's ID."""

     Credential_Exception   = HTTPException(
          status_code    = status.HTTP_401_UNAUTHORIZED,
          detail         = "Invalid Credentials",
          headers        = {"WWW-Authenticate" : "Bearer"},
     )

     try:
          payload   = jwt.decode(token, SECRET_KEY, algorithms= [ALGORITHM])

          id: Optional[int] = payload.get("id")

          if not id:
               raise Credential_Exception
          
          return id
     
     except JWTError:
          raise Credential_Exception
     
def get_location_id(user_location: dict, db):
     """Retrieves an existing location ID or creates a new location record."""
     
     city      = user_location.get("city")
     state     = user_location.get("state")

     existing_location = db.query(Location).filter(Location.city == city,Location.state == state).first()

     if existing_location:
          return existing_location.id
     
     new_location   = Location(
          city      = city,
          state     = state 
     )

     try:
          db.add(new_location)
          db.commit()
          db.refresh(new_location)
          return new_location.id
     
     except Exception as e:
          db.rollback()
          print(e)
          raise HTTPException(
               status_code    = status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail         = "Internal Server Error"   
          )