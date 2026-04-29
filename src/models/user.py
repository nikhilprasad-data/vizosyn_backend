from src.config.settings import Base
from sqlalchemy import Column, Integer,String, Boolean, DateTime
from sqlalchemy.sql import func

class User(Base):

     """Core authentication entity storing primary credentials and account status."""

     __tablename__       = 'users'
     __table_args__     = {'schema' : 'master'}

     id             = Column(Integer, primary_key= True)

     username       = Column(String, unique= True, nullable= False, index= True)

     email          = Column(String, unique= True, nullable= False, index= True)

     password_hash  = Column(String, nullable= False)

     is_active      = Column(Boolean, default= True)

     created_at     = Column(DateTime, server_default= func.now())