from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from src.config.database import Config
from typing import Optional
from src.models import Skill
from sqlalchemy.orm import Session

oauth2passwordbearer = OAuth2PasswordBearer(tokenUrl= '/auth/login')

SECRET_KEY=Config.SECRET_KEY
ALGORITHM=Config.ALGORITHM

def get_id(token: str= Depends(oauth2passwordbearer)):
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

def skill_to_add(db: Session, skill_name_lst: list[str]):
     clean_skill_name_lst = [ skill_name.strip().title() for skill_name in skill_name_lst]

     try:
          existing_skill      = db.query(Skill).filter(Skill.skill_name.in_(clean_skill_name_lst)).all()

          existing_skill_name = [skill.skill_name for skill in existing_skill]

          final_skill_id      = [skill.id for skill in existing_skill]

          create_skill = []

          for skill_name in clean_skill_name_lst:

               if skill_name not in existing_skill_name:

                    create_skill.append(Skill(skill_name= skill_name))
          
          if create_skill:
               db.add_all(create_skill)
               db.flush()

               for new_skill in create_skill:
                    final_skill_id.append(new_skill.id)
          
          return final_skill_id
     
     except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error while verifying skills."
        )