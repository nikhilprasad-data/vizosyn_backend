from src.config.settings import Base
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func

class TeamMember(Base):

     """Tracks active participants within a team, linking users to their collaboration groups."""

     __tablename__  = 'team_members'
     __table_args__ = {'schema' : 'collaboration'}

     id        = Column(Integer, primary_key= True)

     team_id   = Column(Integer, ForeignKey('collaboration.teams.id'))

     user_id   = Column(Integer, ForeignKey('master.users.id'))

     is_active = Column(Boolean, default= True)

     joined_at = Column(DateTime, server_default= func.now())