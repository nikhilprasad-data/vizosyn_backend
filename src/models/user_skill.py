from src.config.settings import Base
from sqlalchemy import Column, Integer, ForeignKey, String

class UserSkill(Base):

     """Association table mapping users to their acquired skills (Many-to-Many relationship)."""

     __tablename__       = 'user_skills'
     __table_args__     = {'schema' : 'master'}

     user_id   = Column(Integer, ForeignKey('master.users.id'), primary_key= True)

     skill_id  = Column(Integer, ForeignKey('master.skills.id'), primary_key= True)