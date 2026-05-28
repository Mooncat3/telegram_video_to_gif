from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bot.db")
    default_lang: str = os.getenv("DEFAULT_LANG", "en")
    max_input_mb: int = int(os.getenv("MAX_INPUT_MB", 20))
    temp_dir: str = os.getenv("TEMP_DIR", "./tmp")
    ffmpeg_path: str = os.getenv("FFMPEG_PATH", "ffmpeg")
    admin_ids: tuple[int, ...] = tuple(int(x) for x in os.getenv("ADMINS", "").split(",") if x)


settings = Settings()
