from aiogram import Router, types
from aiogram.filters import Command
from db.repo import Repo

from db import Session

router = Router()


@router.message(Command("whitelist"))
async def whitelist(message: types.Message):
    args = message.text.split()[1:] if len(message.text.split()) > 1 else None

    async with Session() as s:
        repo = Repo(s)
        if await repo.is_admin(message.from_user.id) and args and len(args) == 2:
            operation_name, _user_id = args

            if operation_name == "add":
                await repo.add_to_whitelist(_user_id)
            elif operation_name == "remove":
                await repo.remove_from_whitelist(_user_id)
