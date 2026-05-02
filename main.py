from fastapi import FastAPI
from src.routes import auth, profile, skill, team_request, team, user_skill
# from src.config.settings import Base,engine
from fastapi.middleware.cors import CORSMiddleware

# Base.metadata.create_all(bind= engine)

app = FastAPI()

app.add_middleware(
     CORSMiddleware,
     allow_origins  = ["http://localhost:3000","https://vizosyn-frontend.vercel.app"],
     allow_credentials= True,
     allow_methods    = ["*"],
     allow_headers    = ["*"]
)
app.include_router(auth, prefix= "/api/auth", tags= ["Auths"])
app.include_router(profile, prefix= "/api/profile", tags= ["Profile"])
app.include_router(skill, prefix="/api/skill", tags= ["Skill"])
app.include_router(team, prefix= "/api/team", tags= ["Team"])
app.include_router(team_request, prefix= "/api/team-request", tags= ["Team-Request"])
app.include_router(user_skill,prefix= "/api/user-skill", tags= ["User-Skill"])