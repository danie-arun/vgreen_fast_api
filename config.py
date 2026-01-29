from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    
    DATABASE_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
