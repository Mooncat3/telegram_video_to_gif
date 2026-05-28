import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import settings
from core.logger import logger
from handlers import (start as h_start, settings as h_settings, video as h_video, admin as h_admin, errors as h_errors,
                      whitelist as h_whitelist)


async def main():
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(h_start.router)
    dp.include_router(h_whitelist.router)
    dp.include_router(h_settings.router)
    dp.include_router(h_video.router)
    dp.include_router(h_admin.router)
    dp.include_router(h_errors.router)
    logger.info("Bot started")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bye")
