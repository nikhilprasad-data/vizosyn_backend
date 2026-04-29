from src.config.settings import Base
from sqlalchemy import Column, Integer,String

class Skill(Base):

     """Dynamic catalog of technical skills added and shared by users across the platform."""

     __tablename__       = 'skills'
     __table_args__     = {'schema' : 'master'}

     id             = Column(Integer, primary_key= True)

     skill_name     = Column(String, unique= True, index= True, nullable= False)