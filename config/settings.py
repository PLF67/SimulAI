from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""

    # Application
    app_name: str = "SimulAI Business Game"
    debug: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/simulai.db"

    # Game settings
    initial_player_money: float = 100000.0
    quarters_per_game: int = 12

    # AI settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ai_provider: str = "anthropic"  # or "openai"

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Frontend ports
    player_frontend_port: int = 8501
    gamemaster_frontend_port: int = 8502
    dashboard_frontend_port: int = 8503

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
