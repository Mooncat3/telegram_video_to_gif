from aiogram.utils.keyboard import InlineKeyboardBuilder

PRESETS = {
    "discord": 10,
    "whatsapp": 16,
    "telegram": 50,
}

LANGS = ["ru", "en"]


def settings_menu(user_lang: str, i18n):
    kb = InlineKeyboardBuilder()
    kb.button(text=i18n.t("preset_discord", user_lang), callback_data="preset:discord")
    kb.button(text=i18n.t("preset_whatsapp", user_lang), callback_data="preset:whatsapp")
    kb.button(text=i18n.t("preset_telegram", user_lang), callback_data="preset:telegram")
    kb.button(text=i18n.t("enter_custom", user_lang), callback_data="enter_custom")
    kb.button(text=i18n.t("change_lang", user_lang), callback_data="change_lang")
    kb.adjust(1)
    return kb.as_markup()


def lang_menu(current: str):
    kb = InlineKeyboardBuilder()
    for lang in LANGS:
        label = ("✅ " if lang == current else "") + lang.upper()
        kb.button(text=label, callback_data=f"lang:{lang}")
    kb.adjust(2)
    return kb.as_markup()
