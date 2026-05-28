from __future__ import annotations

from aiogram import Router, types, F
from aiogram.filters import Command

from db import Session
from db.repo import Repo
from keyboards.admin import admin_menu, pagination
from utils.pagination import split_pages

router = Router()


@router.message(Command("admin"))
async def admin_root(message: types.Message):
    async with Session() as s:
        repo = Repo(s)
        if not await repo.is_admin(message.from_user.id):
            await message.reply("Admins only.")
            return
    await message.reply("Admin panel:", reply_markup=admin_menu())


@router.callback_query(F.data == "admin:stats")
async def admin_stats(call: types.CallbackQuery):
    async with Session() as s:
        repo = Repo(s)
        if not await repo.is_admin(call.from_user.id):
            await call.answer("Admins only.")
            return
        # quick and dirty: read global stats row
        from db.models import GlobalStats
        gs = await s.get(GlobalStats, 1)
        total = gs.total_conversions if gs else 0
    await call.message.edit_text(f"Total conversions: {total}")
    await call.answer()


@router.callback_query(F.data.startswith("admin:users:"))
async def admin_users(call: types.CallbackQuery):
    page = int(call.data.split(":")[-1])
    per_page = 10
    async with Session() as s:
        repo = Repo(s)
        if not await repo.is_admin(call.from_user.id):
            await call.answer("Admins only.")
            return
        total = await repo.count_users()
        total_pages = split_pages(total, per_page)
        users = await repo.list_users(offset=page * per_page, limit=per_page)
        lines = ["ID | username | processed | created"]
        for u in users:
            lines.append(f"{u.id} | @{u.username or '-'} | {u.processed_count} | {u.created_at:%Y-%m-%d}")
        text = "\n".join(lines) or "No users"
    await call.message.edit_text(text, reply_markup=pagination("admin:users", page, total_pages))
    await call.answer()
