import os
import subprocess
from pathlib import Path
from typing import Any, List, Optional, Union

from pydantic import BaseSettings

_base_path = Path(__file__).resolve().parent


class Settings(BaseSettings):
    DEBUG: bool = True

    NOTES_SAVE_BASE_PATH: Path = Path("/tmp/notes")

    JWT_SECRET_KEY: str = "CHANGE_ME_OR_DIE13434523465"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 2  # two days

    class Config:
        env_prefix = ""
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
