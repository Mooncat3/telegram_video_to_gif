from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery

from config import settings
from core.i18n import I18n
from db import Session
from db.repo import Repo
from keyboards.common import settings_menu, lang_menu, PRESETS

i18n = I18n("locales", default_lang=settings.default_lang)


class SettingsForm(StatesGroup):
    waiting_custom_mb = State()


router = Router()


@router.callback_query(F.data.startswith("preset:"))
async def preset_cb(call: CallbackQuery):
    preset = call.data.split(":", 1)[1]
    async with Session() as s:
        repo = Repo(s)
        user = await repo.get_or_create_user(call.from_user.id, call.from_user.full_name, call.from_user.username,
                                             settings.default_lang)
        mb = PRESETS.get(preset, 10)
        await repo.update_limit(user.id, mb)
        await call.message.edit_text(i18n.t("saved", user.lang) + f" — {mb} MB",
                                     reply_markup=settings_menu(user.lang, i18n))
    await call.answer()


@router.callback_query(F.data == "enter_custom")
async def enter_custom(call: CallbackQuery, state: FSMContext):
    async with Session() as s:
        user = await Repo(s).get_or_create_user(call.from_user.id, call.from_user.full_name, call.from_user.username,
                                                settings.default_lang)
    await call.message.edit_text(i18n.t("ask_custom", user.lang))
    await state.set_state(SettingsForm.waiting_custom_mb)


@router.message(SettingsForm.waiting_custom_mb, F.text.regexp(r"^\d{1,3}$"))
async def set_custom_mb(message: types.Message, state: FSMContext):
    mb = int(message.text)
    if not 1 <= mb <= 50:
        await message.answer("1–50 MB")
        return
    async with Session() as s:
        repo = Repo(s)
        user = await repo.get_or_create_user(message.from_user.id, message.from_user.full_name,
                                             message.from_user.username, settings.default_lang)
        await repo.update_limit(user.id, mb)
    await message.answer(i18n.t("saved", user.lang) + f" — {mb} MB", reply_markup=settings_menu(user.lang, i18n))
    await state.clear()


@router.callback_query(F.data == "change_lang")
async def change_lang(call: CallbackQuery):
    async with Session() as s:
        user = await Repo(s).get_or_create_user(call.from_user.id, call.from_user.full_name, call.from_user.username,
                                                settings.default_lang)
    await call.message.edit_reply_markup(reply_markup=lang_menu(user.lang))
    await call.answer()


@router.callback_query(F.data.startswith("lang:"))
async def set_lang(call: CallbackQuery):
    lang = call.data.split(":", 1)[1]
    async with Session() as s:
        repo = Repo(s)
        await repo.update_lang(call.from_user.id, lang)
        await repo.get_or_create_user(call.from_user.id, call.from_user.full_name, call.from_user.username,
                                      settings.default_lang)
    await call.message.edit_text(i18n.t("saved", lang), reply_markup=settings_menu(lang, i18n))
    await call.answer()
