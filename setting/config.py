import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from functools import lru_cache

# Determine the environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

# Load the corresponding .env file
env_path = Path(f".env.{ENVIRONMENT}")
if env_path.exists():
    load_dotenv(env_path)
    print('env_path: ', env_path)


class Settings(BaseSettings):
    pg_user: str 
    pg_password: str
    pg_host: str
    pg_port: str
    pg_database: str
    
    cors_origins: list[str] = ["http://localhost:3000"]
    debug: bool = False
    
@lru_cache()
def get_settings():
    return Settings()