from src.config.settings import Base
from sqlalchemy import Column, Integer,String
class Location(Base):

     """Represents geographical locations (City, State) for users across the platform."""
     
     __tablename__       = 'locations'
     __table_args__     = {'schema' : 'master'} 

     id        = Column(Integer, primary_key= True)

     city      = Column(String, nullable= False, index= True)

     state     = Column(String, nullable= False)