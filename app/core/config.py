import os
from dotenv import load_dotenv #type:ignore

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Event AI Generator"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Groq API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    
    # Hugging Face Configuration
    HF_API_TOKEN: str = os.getenv("HF_API_TOKEN")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./event_ai.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()