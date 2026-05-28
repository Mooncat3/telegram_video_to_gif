from aiogram import Router, types
from aiogram.filters import CommandStart, Command

from config import settings
from core.i18n import I18n
from db import Session
from db.repo import Repo
from keyboards.common import settings_menu

i18n = I18n("locales", default_lang=settings.default_lang)

router = Router()


async def menu(message: types.Message):
    async with Session() as s:
        repo = Repo(s)
        user = await repo.get_or_create_user(
            message.from_user.id,
            message.from_user.full_name,
            message.from_user.username,
            settings.default_lang,
        )
    title = i18n.t("start_title", user.lang)
    body = i18n.t("start_body", user.lang)
    txt = f"{title}\n\n{body}\n\n" + i18n.t("current_limit", user.lang).format(mb=user.file_limit_mb) + "\n" + i18n.t(
        "current_lang", user.lang).format(lang=user.lang.upper())
    await message.answer(txt, reply_markup=settings_menu(user.lang, i18n))


@router.message(CommandStart())
async def start(message: types.Message):
    return await menu(message)


@router.message(Command("menu"))
async def menu_command(message: types.Message):
    return await menu(message)
