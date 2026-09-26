from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


class Settings(BaseSettings):
    app_name: str = Field(default="FitBuddy – AI Fitness Plan Generator", alias="APP_NAME")
    host: str = Field(default="127.0.0.1", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    database_url: str = Field(default="sqlite:///./data/fitbuddy.db", alias="DATABASE_URL")

    demo_mode: bool = Field(default=True, alias="DEMO_MODE")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_workout_model: str = Field(default="gemini-3.6-flash", alias="GEMINI_WORKOUT_MODEL")
    gemini_tip_model: str = Field(default="gemini-3.6-flash", alias="GEMINI_TIP_MODEL")

    admin_username: str = Field(default="admin", alias="ADMIN_USERNAME")
    admin_password: str = Field(default="fitbuddy123", alias="ADMIN_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

print("DEMO_MODE =", settings.demo_mode)
print("API_KEY_FOUND =", bool(settings.gemini_api_key))

