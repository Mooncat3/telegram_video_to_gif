from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="👥 Users", callback_data="admin:users:0")
    kb.button(text="📈 Stats", callback_data="admin:stats")
    kb.adjust(2)
    return kb.as_markup()


def pagination(prefix: str, page: int, total_pages: int):
    kb = InlineKeyboardBuilder()
    if page > 0:
        kb.button(text="⬅️", callback_data=f"{prefix}:{page - 1}")
    kb.button(text=f"{page + 1}/{total_pages}", callback_data="noop")
    if page + 1 < total_pages:
        kb.button(text="➡️", callback_data=f"{prefix}:{page + 1}")
    kb.adjust(3)
    return kb.as_markup()
