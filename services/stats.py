from __future__ import annotations

from db.repo import Repo


async def on_success(repo: Repo, user_id: int):
    await repo.inc_user_counter(user_id)
    await repo.inc_global_counter()
