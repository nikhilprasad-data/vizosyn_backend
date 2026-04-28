import os
from dotenv import load_dotenv

# Load secrets from local .env file into the environment
load_dotenv()

class Config:

     """Centralized configuration variables for VizoSyn backend."""
     
     SQLALCHEMY_DATABASE_URI            = os.environ.get("DATABASE_URI", "")

     SECRET_KEY                         = os.environ.get("JWT_SECRET_KEY", "")

     TOKEN_EXPIRATION_TIME              = int(os.environ.get("JWT_TOKEN_EXPIRATION_TIME_MINUTES", "30"))

     ALGORITHM                          = os.environ.get("ALGORITHM","HS256")