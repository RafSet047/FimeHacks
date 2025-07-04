from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import List, Optional
import os


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    database_url: str = "sqlite:///./app.db"
    database_echo: bool = False
    
    storage_path: str = "./storage"
    max_file_size: int = 104857600
    allowed_file_types: str = "txt,pdf,doc,docx,png,jpg,jpeg,gif,mp3,wav,mp4,avi,mov"
    
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    chroma_persist_directory: str = "./chroma_db"
    
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    app_name: str = "SuperIntelligence AI System"
    app_version: str = "1.0.0"
    debug: bool = True
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.allowed_file_types.split(",")]
    
    def create_directories(self):
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        os.makedirs(self.chroma_persist_directory, exist_ok=True)


settings = Settings() 