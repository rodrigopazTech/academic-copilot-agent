import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Academic Copilot Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Agent Execution Mode (Mock/Live)
    MOCK_MODE: bool = True

    # LLM Settings
    DEFAULT_LLM_PROVIDER: str = "openai"  # "openai" or "google-genai"
    OPENAI_API_KEY: str = Field(default="", alias="OPENAI_API_KEY")
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"
    
    GEMINI_API_KEY: str = Field(default="", alias="GEMINI_API_KEY")
    GEMINI_MODEL_NAME: str = "gemini-2.0-flash"

    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "app" / "data"
    SYLLABI_DIR: Path = BASE_DIR / "app" / "data" / "sample_syllabi"
    TRANSCRIPTS_DIR: Path = BASE_DIR / "app" / "data" / "sample_transcripts"
    REPORTS_DIR: Path = BASE_DIR / "generated_reports"

    # Optional Google Workspace
    GOOGLE_CLIENT_SECRET_PATH: str = "config/client_secret.json"
    GOOGLE_TOKEN_PATH: str = "config/token.json"

settings = Settings()
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
