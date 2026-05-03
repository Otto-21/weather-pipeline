from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    openweather_api_key: str
    collect_interval_minutes: int = 10
    data_dir: Path = Path("data")

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def curated_dir(self) -> Path:
        return self.data_dir / "curated"
    
    class Config:
        env_file = ".env"

settings = Settings()

settings.raw_dir.mkdir(parents=True, exist_ok=True)
settings.curated_dir.mkdir(parents=True, exist_ok=True)