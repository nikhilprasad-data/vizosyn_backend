from passlib.context import CryptContext
from datetime import datetime, timedelta
from src.config.database import Config
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status ,HTTPException
from typing import Optional

password_context    = CryptContext(schemes= ["bcrypt"], deprecated= ["auto"])

def generate_password_hash(plain_password: str):
     """Generates a bcrypt hash for a given plaintext password."""

     return password_context.hash(plain_password)

def check_password_hash(plain_password: str, hash_password: str):
     """Verifies a plaintext password against its stored bcrypt hash."""
     return password_context.verify(plain_password, hash_password)


SECRET_KEY     = Config.SECRET_KEY

exp_time       = Config.TOKEN_EXPIRATION_TIME

ALGORITHM      = Config.ALGORITHM

def create_access_token(identity: dict):
     """Generates a JWT access token with an expiration timestamp."""

     to_encode = identity.copy()

     expire_time       = datetime.utcnow() + timedelta(minutes= exp_time) 

     to_encode.update({"exp" : expire_time})

     access_token = jwt.encode(to_encode, SECRET_KEY, algorithm= ALGORITHM)

     return access_token


oauth2passwordbearer = OAuth2PasswordBearer(tokenUrl= '/auth/login')

def get_info(token: str= Depends(oauth2passwordbearer)):
     """Validates the JWT token and extracts the user identity payload."""
     
     Credential_Exception     = HTTPException(
          status_code         = status.HTTP_401_UNAUTHORIZED,
          detail              = "Invalid Credentials",
          headers             = {"WWW-Autenticate" : "Bearer"},
     )
     try:
          payload   = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

          id: Optional[int] = payload.get("id")

          username: Optional[str] = payload.get("username")

          if not (id and username):
               raise Credential_Exception
          
          return {"id" : id, "username" : username}

     except JWTError:
          raise Credential_Exception