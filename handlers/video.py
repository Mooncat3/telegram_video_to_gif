from __future__ import annotations

import os
import time
from typing import List

from aiogram import Router, types, F
from aiogram.types import FSInputFile
from aiogram.utils.chat_action import ChatActionSender

from config import settings
from core.i18n import I18n
from core.logger import logger
from db import Session
from db.repo import Repo
from services.ffmpeg import video_to_gif
from services.files import temp_path
from services.stats import on_success
from services.validators import sanitize_filename
from aiogram_media_group import media_group_handler

router = Router()
i18n = I18n("locales", default_lang=settings.default_lang)

MAX_INPUT_BYTES = settings.max_input_mb * 1024 * 1024


def rand_name():
    return str(time.time() * 1000).split(".")[0]


def cleanup_files(dl_path=None, out_path=None):
    try:
        if dl_path:
            os.remove(dl_path)
    except OSError:
        pass
    try:
        if out_path:
            os.remove(out_path)
    except OSError:
        pass


async def send_document(message: types.Message, lang: str, file_info: dict, dl_path: str, out_path: str = None):
    # Send back as document (file), not as GIF animation, to preserve quality
    try:
        file_info_str = (f"({file_info['width']}px, {file_info['fps']} FPS, "
                         f"{round(file_info['size'] / 1024 / 1024, 2)} MB)")
        await message.bot.send_document(message.chat.id, disable_content_type_detection=True,
                                        caption=f"{i18n.t("done", lang)} {file_info_str}", request_timeout=120,
                                        document=FSInputFile(out_path or dl_path),
                                        reply_to_message_id=message.message_id)
    finally:
        # Stats & cleanup
        async with Session() as s:
            await on_success(Repo(s), message.from_user.id)
        cleanup_files(dl_path, out_path)


@router.message(F.media_group_id,
                F.content_type.in_({"video", "document", "sticker", "video_note", "photo"}))
@media_group_handler
async def handle_many_medias(messages: List[types.Message]):
    if len(messages) == 0:
        return
    message = messages[0]
    async with Session() as s:
        repo = Repo(s)
        if not await repo.is_in_whitelist(message.from_user.id):
            return
        user = await repo.get_or_create_user(message.from_user.id, message.from_user.full_name,
                                             message.from_user.username, settings.default_lang)
        lang = user.lang
    await message.reply(i18n.t("err_many_files", lang))


async def update_busy(user_id: int, busy: bool):
    async with Session() as s:
        repo = Repo(s)
        user = await repo.get_or_create_user(user_id)
        if user:
            await repo.update_busy(user_id, busy)


@router.message(F.video | F.document | F.sticker | F.video_note | F.photo)
async def handle_media(message: types.Message):
    try:
        async with Session() as s:
            repo = Repo(s)
            if not await repo.is_in_whitelist(message.from_user.id):
                return
            user = await repo.get_or_create_user(message.from_user.id)
            if user and user.busy:
                return await message.reply(i18n.t("err_busy", user.lang))

        await update_busy(message.from_user.id, True)
        await handle_media_(message)
        await update_busy(message.from_user.id, False)
    except:
        await update_busy(message.from_user.id, False)


async def handle_media_(message: types.Message):
    # Collect attachments
    attachments = []
    file_id = None
    file_name = ""
    mime_type = None
    size = None

    if message.video:
        v = message.video
        attachments.append((v.mime_type or "video/unknown", v.file_size))
        file_id = v.file_id
        file_name = sanitize_filename(v.file_name or rand_name())
        mime_type = v.mime_type
        size = v.file_size
    elif message.document:
        d = message.document
        attachments.append((d.mime_type or "application/octet-stream", d.file_size))
        file_id = d.file_id
        file_name = sanitize_filename(d.file_name or rand_name())
        mime_type = d.mime_type
        size = d.file_size
    elif message.sticker:
        s = message.sticker
        mime_type = "video/webm"
        attachments.append((mime_type, s.file_size))
        file_id = s.file_id
        file_name = sanitize_filename(s.file_unique_id)
        size = s.file_size
    elif message.video_note:
        n = message.video_note
        mime_type = "video/mp4"
        attachments.append((mime_type, n.file_size))
        file_id = n.file_id
        file_name = sanitize_filename(n.file_unique_id)
        size = n.file_size
    elif message.photo:
        p = message.photo[-1]
        mime_type = "image/jpeg"
        attachments.append((mime_type, p.file_size))
        file_id = p.file_id
        file_name = sanitize_filename(p.file_unique_id)
        size = p.file_size

    # Get user settings
    async with Session() as s:
        repo = Repo(s)
        user = await repo.get_or_create_user(message.from_user.id, message.from_user.full_name,
                                             message.from_user.username, settings.default_lang)
        target_mb = user.file_limit_mb
        lang = user.lang

    # Validate single video
    if len(attachments) != 1 or not mime_type or not (mime_type.startswith("video/") or mime_type.startswith("image/")):
        await message.reply(i18n.t("err_not_video", lang))
        return

    # Size check
    if size and size > MAX_INPUT_BYTES:
        await message.reply(i18n.t("err_too_big_input", lang).format(mb=settings.max_input_mb))
        return

    await message.reply(f"{i18n.t('processing', lang)} (≤ {target_mb} MB)")

    # Download to temp
    dl_path = temp_path(f"{rand_name()}_{file_name}")
    try:
        await message.bot.download(file_id, destination=dl_path, timeout=120)
    except:
        logger.exception(f"{message.from_user.id}: Download failed")
        await message.reply(i18n.t('err_download_media', lang))
        cleanup_files(dl_path)
        return

    async def process_error(error: Exception):
        logger.exception(f"{message.from_user.id}: Conversion failed")
        async with Session() as s_:
            repo_ = Repo(s_)
            if await repo_.is_admin(message.from_user.id):
                await message.reply(f"Error: {error}")
            else:
                await message.reply(i18n.t('err_conversion', lang))
        cleanup_files(dl_path, out_path)

    # Convert
    out_path = temp_path(f"{rand_name()}_{os.path.splitext(file_name)[0]}.gif")
    try:
        async with ChatActionSender.upload_document(message.chat.id, message.bot):
            file_info = await video_to_gif(dl_path, out_path, size_limit_mb=target_mb)
    except Exception as e:
        return await process_error(e)

    try:
        logger.info(f"Sending to {message.from_user.id}...")
        await send_document(message, lang, file_info, dl_path, out_path)
        logger.info(f"Sent to {message.from_user.id}")
    except Exception as e:
        return await process_error(e)
