from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from src.config.database import Config
from typing import Optional

oauth2passwordbearer = OAuth2PasswordBearer(tokenUrl= '/auth/login')

SECRET_KEY=Config.SECRET_KEY
ALGORITHM=Config.ALGORITHM

def get_id(token: str= Depends(oauth2passwordbearer)):
     """Extracts and validates the authenticated user ID from the provided JWT token."""
     
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