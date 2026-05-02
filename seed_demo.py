"""
Database Seeding Script for VizoSyn– Skill-Based Teammate Matchmaking Platform
Populates the database with three distinct user personas (Admin, Applicant, New User) 
to facilitate end-to-end testing of the team management and onboarding pipelines.
"""

from src.models import User, Location, Profile,Skill, UserSkill, Team, TeamRequest, TeamMember
from src.config.database import Config
from src.config.settings import SessionLocal
from src.services import generate_password_hash, get_location_id,skill_to_add

#from src.config.settings import engine, Base

#Base.metadata.create_all(bind= engine)

db = SessionLocal()

demo_username_1          = "admin_demo"
demo_email_1             = "admin_demo@vizosyn.com"
demo_password_hash_1     = generate_password_hash("demo_password_1")
demo_full_name_1         = "Admin Demo"
demo_bio_1               = "Full Stack Devloper"
demo_github_url_1        = "https://github.com/admin_demo"
demo_linkedin_url_1      = "https://www.linkedin.com/in/admin_demo"
demo1_skill_name         = ["Next.js", "Python", "FastAPI"]
demo_team_name_1         = "Coder Analyst"
demo_description_1       = "Product Devloper"


demo_username_2          = "teammate_demo"
demo_email_2             = "teammate_demo@vizosyn.com"
demo_password_hash_2     = generate_password_hash("demo_password_2")
demo_full_name_2         = "Teammate Demo"
demo_bio_2               = "Back-end Devloper"
demo_github_url_2        = "https://github.com/teammate_demo"
demo_linkedin_url_2      = "https://www.linkedin.com/in/teammate_demo"
demo2_skill_name         = ["Python", "FastAPI"]


demo_username_3          = "fresh_demo"
demo_email_3             = "fresh_demo@vizosyn.com"
demo_password_hash_3     = generate_password_hash("demo_password_3")

demo_location  = { "city" : "New Delhi", "state" : "Delhi"}

existing_location_id = get_location_id(db= db, user_location= demo_location)

demo1_skill_id = skill_to_add(skill_name_lst= demo1_skill_name, db= db)

demo2_skill_id = skill_to_add(skill_name_lst= demo2_skill_name, db= db)

# Persona 1: Fully onboarded admin user with an active profile, skills, and ownership of an existing team.
existing_demo_1 = db.query(User).filter(User.username == demo_username_1, User.email == demo_email_1, User.is_active == True).first()
if existing_demo_1:
     print("admin_demo already exists.")

else:
     demo1 = User(
          username       = "admin_demo",
          email          = "admin_demo@vizosyn.com",
          password_hash  = demo_password_hash_1 
     )

     db.add(demo1)
     db.flush()

     print("admin_demo user created successfully.")

     demo_profile_1    = Profile(
          user_id        = demo1.id,
          location_id    = existing_location_id,
          full_name      = demo_full_name_1,
          bio            = demo_bio_1,
          github_url     = demo_github_url_1,
          linkedin_url   = demo_linkedin_url_1 ,
     )
     db.add(demo_profile_1)
     db.flush()

     print("admin_demo profile created successfully.")

     demo_skill_1 = []
     for s_id in demo1_skill_id:
          demo_skill_1.append(UserSkill(user_id= demo1.id, skill_id= s_id))

     db.add_all(demo_skill_1)
     db.flush()

     print("admin_demo skills added successfully.")
     
     demo_team_1    = Team(
          name           = demo_team_name_1,
          description    = demo_description_1,
          admin_id       = demo1.id
     )
     db.add(demo_team_1)
     db.flush()

     print("team_demo team created successfully.")

     demo_admin_member   = TeamMember(
          team_id        = demo_team_1.id,
          user_id        = demo1.id,
          is_active      = True
     )
     db.add(demo_admin_member)
     db.commit()

# Persona 2: Fully onboarded user with profile and skills, configured to test the "Join Team" request flow.
existing_demo_2 = db.query(User).filter(User.username == demo_username_2, User.email == demo_email_2, User.is_active == True).first()
if existing_demo_2:
     print("teammate_demo already exists.")

else:
     demo2 = User(
          username       = "teammate_demo",
          email          = "teammate_demo@vizosyn.com",
          password_hash  = demo_password_hash_2
     )
     db.add(demo2)
     db.flush()

     print("teammate_demo user created successfully.")

     demo_profile_2    = Profile(
          user_id        = demo2.id,
          location_id    = existing_location_id,
          full_name      = demo_full_name_2,
          bio            = demo_bio_2,
          github_url     = demo_github_url_2,
          linkedin_url   = demo_linkedin_url_2,
     )
     db.add(demo_profile_2)
     db.flush()

     print("teammate_demo profile created successfully.")

     demo_skill_2 = []
     for s_id in demo2_skill_id:
          demo_skill_2.append(UserSkill(user_id= demo2.id, skill_id= s_id))

     db.add_all(demo_skill_2)
     db.commit()

     print("teammate_demo skills added successfully.")
     
# Persona 3: Blank slate user account to demonstrate the initial profile creation and onboarding experience.
existing_demo_3 = db.query(User).filter(User.username == demo_username_3, User.email == demo_email_3, User.is_active == True).first()
if existing_demo_3:
     print("fresh_demo already exists.")

else:
     demo3 = User(
          username       = "fresh_demo",
          email          = "fresh_demo@vizosyn.com",
          password_hash  = demo_password_hash_3
     )
     db.add(demo3)
     db.commit()
     print("fresh_demo created successfully.")

db.close()
print("Seed script completed securely.")