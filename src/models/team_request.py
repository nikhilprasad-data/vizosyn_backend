from src.config.settings import Base
from sqlalchemy import Column, Integer,String, ForeignKey, Text,DateTime, CheckConstraint
from sqlalchemy.sql import func

class TeamRequest(Base):

     """Manages the lifecycle of team join requests, including status and applicant messages."""

     __tablename__  = 'team_requests'
     __table_args__ = {'schema' : 'collaboration'}

     id             = Column(Integer, primary_key= True)

     team_id        = Column(Integer, ForeignKey('collaboration.teams.id'))

     user_id        = Column(Integer, ForeignKey('master.users.id'))

     status         = Column(String, CheckConstraint("status IN ('Pending', 'Accepted','Rejected')"), default= 'Pending')

     message        = Column(Text)

     requested_at   = Column(DateTime, server_default= func.now())