import os
from dotenv import load_dotenv #type: ignore

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Event AI Generator"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Groq API Configuration - ADD DEBUGGING
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    
    # Hugging Face Configuration
    HF_API_TOKEN: str = os.getenv("HF_API_TOKEN", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./event_ai.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    def __init__(self):
        """Debug environment variables on initialization"""
        print("🔍 Environment Variables Debug:")
        print(f"   GROQ_API_KEY loaded: {bool(self.GROQ_API_KEY)}")
        print(f"   GROQ_API_KEY length: {len(self.GROQ_API_KEY)}")
        print(f"   GROQ_API_KEY starts with 'gsk_': {self.GROQ_API_KEY.startswith('gsk_') if self.GROQ_API_KEY else False}")
        print(f"   HF_API_TOKEN loaded: {bool(self.HF_API_TOKEN)}")

settings = Settings()