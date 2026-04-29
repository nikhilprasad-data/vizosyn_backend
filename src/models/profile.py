from src.config.settings import Base
from sqlalchemy import Column, Integer,String,Text, ForeignKey, Boolean

class Profile(Base):

     """Stores detailed public profiles and professional links linked to a specific user account."""
     
     __tablename__       = 'profiles'
     __table_args__     = {'schema' : 'master'}

     id             = Column(Integer, primary_key= True)

     user_id        = Column(Integer,ForeignKey('master.users.id', ondelete='CASCADE'), unique= True)

     location_id    = Column(Integer, ForeignKey('master.locations.id'))

     full_name      = Column(String, nullable= False)

     bio            = Column(Text)

     github_url     = Column(String)

     linkedin_url   = Column(String)

     is_active      = Column(Boolean, default= True)