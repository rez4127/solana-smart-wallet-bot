from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    telegram_bot_token: str

    # Solana RPC
    solana_rpc_url: str = "https://api.mainnet-beta.solana.com"
    helius_api_key: str | None = None
    custom_rpc_url: str | None = None

    # Bot
    admin_user_ids: str = ""
    max_signatures_per_query: int = 300
    request_timeout: int = 30
    log_level: str = "INFO"

    # Database
    database_path: str = "./data/bot.db"

    @property
    def admin_ids(self) -> List[int]:
        if not self.admin_user_ids.strip():
            return []
        return [int(x.strip()) for x in self.admin_user_ids.split(",") if x.strip().isdigit()]

    @property
    def rpc_url(self) -> str:
        """Priority: Custom > Helius > Public"""
        if self.custom_rpc_url:
            return self.custom_rpc_url
        if self.helius_api_key:
            return f"https://mainnet.helius-rpc.com/?api-key={self.helius_api_key}"
        return self.solana_rpc_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
