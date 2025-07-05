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

    # Database settings
    database_url: str = "sqlite:///./app.db"
    database_echo: bool = False

    # File storage settings
    storage_path: str = "./storage"
    max_file_size: int = 104857600
    allowed_file_types: str = "txt,pdf,doc,docx,png,jpg,jpeg,gif,mp3,wav,mp4,avi,mov"

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    google_generative_ai_api_key: Optional[str] = Field(default=None, alias="GOOGLE_GENERATIVE_AI_API_KEY")
    google_application_credentials: Optional[str] = Field(default=None, alias="GOOGLE_APPLICATION_CREDENTIALS")

    # LLM settings
    llm_model: str = "gemini-2.5-flash"

    # Vector database settings
    chroma_persist_directory: str = "./chroma_db"

    # Collection-specific embedding dimensions
    text_embedding_dimension: int = 1536  # OpenAI text-embedding-3-small or Google embeddings
    audio_embedding_dimension: int = 1536  # Audio transcription → text embeddings

    # Processing settings
    text_chunk_size: int = 500
    text_chunk_overlap: int = 50
    audio_chunk_duration: int = 30  # seconds for audio processing

    # Google API specific settings
    google_speech_language: str = "en-US"
    google_speech_model: str = "latest_long"
    google_embedding_model: str = "models/embedding-001"

    # Transcription settings
    audio_transcription_confidence_threshold: float = 0.8
    enable_speaker_diarization: bool = True
    max_speakers: int = 6

    # Logging settings
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"

    # App settings
    app_name: str = "SuperIntelligence AI System"
    app_version: str = "1.0.0"
    debug: bool = True

    @property
    def allowed_file_types_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.allowed_file_types.split(",")]

    @property
    def text_file_types(self) -> List[str]:
        return ["txt", "pdf", "doc", "docx", "md", "html", "json", "csv"]

    @property
    def audio_file_types(self) -> List[str]:
        return ["mp3", "wav", "m4a", "flac", "ogg"]

    @property
    def document_file_types(self) -> List[str]:
        return ["pdf", "doc", "docx"]

    def create_directories(self):
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        os.makedirs(self.chroma_persist_directory, exist_ok=True)


settings = Settings()
