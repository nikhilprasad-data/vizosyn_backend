from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.ext.declarative import declarative_base
from .database import Config


db_url         = Config.SQLALCHEMY_DATABASE_URI 

engine         = create_engine(db_url)

SessionLocal   = sessionmaker(autocommit= False, autoflush= False, bind= engine)

Base           = declarative_base()

def get_db(): 

     """FastAPI dependency to manage database session."""

     db = SessionLocal()
     try:
          yield db

     finally:
          db.close()