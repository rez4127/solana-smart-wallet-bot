import aiosqlite
from pathlib import Path

from config.settings import get_settings
from utils.logger import logger


async def init_db() -> None:
    settings = get_settings()
    db_path = Path(settings.database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mint TEXT NOT NULL,
                query_date TEXT NOT NULL,
                buyers_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS cached_buyers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mint TEXT NOT NULL,
                query_date TEXT NOT NULL,
                wallet TEXT NOT NULL,
                amount REAL,
                signature TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(mint, query_date, wallet)
            )
            """
        )
        await db.commit()

    logger.info(f"Database initialized at {db_path}")
