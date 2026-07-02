from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    data_dir: Path = Path("data")
    raw_dir: Path = Path("data/raw")
    processed_dir: Path = Path("data/processed")
    gtfs_url: str = "https://romamobilita.it/sites/default/files/rome_static_gtfs.zip"
    database_url: str = "sqlite:///data/processed/rome_twin.sqlite"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

settings = Settings()
