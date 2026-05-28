from aiogram import Router
from aiogram.types import ErrorEvent

from core.logger import logger

router = Router()


@router.errors()
async def on_error(event: ErrorEvent):
    logger.exception("Unhandled error: %s", event.exception)
