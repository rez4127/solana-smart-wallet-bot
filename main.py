import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config.settings import get_settings
from utils.logger import logger
from bot.handlers import start, buyers
from database.models import init_db


async def main() -> None:
    settings = get_settings()

    if not settings.telegram_bot_token or settings.telegram_bot_token == "your_bot_token_here":
        logger.error("TELEGRAM_BOT_TOKEN is not set in .env")
        sys.exit(1)

    # Initialize database
    await init_db()

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers
    dp.include_router(start.router)
    dp.include_router(buyers.router)

    logger.info("Bot is starting...")
    logger.info(f"Using RPC: {settings.rpc_url.split('?')[0]}...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user.")
