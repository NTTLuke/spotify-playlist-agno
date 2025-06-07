from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # App settings
    app_name: str = "Spotify Playlist Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Spotify OAuth settings
    spotify_client_id: Optional[str] = None
    spotify_client_secret: Optional[str] = None
    spotify_redirect_uri: str = "http://localhost:8000/callback"
    spotify_bot_redirect_uri: str = "http://localhost:8000/bot-callback"
    spotify_scope: str = "user-read-private user-read-email playlist-modify-public playlist-modify-private user-top-read user-modify-playback-state user-read-playback-state user-read-recently-played user-follow-read playlist-read-private playlist-read-collaborative"
    spotify_access_token: Optional[str] = None
    
    # Security settings
    secret_key: str = "your-secret-key-here-change-in-production"
    access_token_expire_minutes: int = 60
    
    # CORS settings
    cors_origins: list[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]
    
    # Database settings
    db_url: str = "postgresql://ailuke:mypassword123456@localhost:5432/aimemory"
    postgres_url: Optional[str] = None
    
    # Azure OpenAI settings
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: Optional[str] = None
    azure_deployment_name: Optional[str] = None
    azure_openai_api_version: Optional[str] = None
    
    # Other API keys
    serper_api_key: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()