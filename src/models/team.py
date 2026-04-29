from src.config.settings import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, CheckConstraint, Boolean
from sqlalchemy.sql import func

class Team(Base):

     """Core entity for user-created teams, managing capacity, administration, and recruitment status."""

     __tablename__  = 'teams'
     __table_args__ = {'schema' : 'collaboration'}

     id             = Column(Integer, primary_key= True)

     name           = Column(String, unique= True, nullable= False, index= True)

     description    = Column(Text)

     admin_id       = Column(Integer,ForeignKey('master.users.id'))

     max_members    = Column(Integer, default= 5)

     created_at     = Column(DateTime, server_default= func.now()) 

     status         = Column(String, CheckConstraint("status IN ('Open', 'Full')"), default= 'Open')

     is_active      = Column(Boolean, default= True) 