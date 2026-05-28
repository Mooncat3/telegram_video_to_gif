from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, GlobalStats, Admin, Whitelist


class Repo:
    def __init__(self, session: AsyncSession):
        self.s = session

    async def get_or_create_user(self, user_id: int, nickname: str | None = None, username: str | None = None,
                                 default_lang: str = "en", default_limit_mb: int = 10) -> User:
        user = await self.s.get(User, user_id)
        if user is None:
            user = User(id=user_id, nickname=nickname, username=username, lang=default_lang,
                        file_limit_mb=default_limit_mb)
            self.s.add(user)
            # ensure global stats row exists
            if await self.s.get(GlobalStats, 1) is None:
                self.s.add(GlobalStats(id=1, total_conversions=0))
            await self.s.commit()
        return user

    async def update_lang(self, user_id: int, lang: str):
        await self.s.execute(update(User).where(User.id == user_id).values(lang=lang))
        await self.s.commit()

    async def update_limit(self, user_id: int, mb: int):
        await self.s.execute(update(User).where(User.id == user_id).values(file_limit_mb=mb))
        await self.s.commit()

    async def inc_user_counter(self, user_id: int):
        await self.s.execute(update(User).where(User.id == user_id).values(processed_count=User.processed_count + 1))
        await self.s.commit()

    async def inc_global_counter(self):
        gs = await self.s.get(GlobalStats, 1)
        if gs is None:
            gs = GlobalStats(id=1, total_conversions=0)
            self.s.add(gs)
        gs.total_conversions += 1
        await self.s.commit()

    async def list_users(self, offset: int, limit: int = 10):
        q = await self.s.execute(select(User).order_by(User.created_at.desc()).offset(offset).limit(limit))
        return q.scalars().all()

    async def count_users(self) -> int:
        q = await self.s.execute(select(User))
        return len(q.scalars().all())

    async def is_admin(self, user_id: int) -> bool:
        return (await self.s.get(Admin, user_id)) is not None

    async def is_in_whitelist(self, user_id: int) -> bool:
        return (await self.s.get(Whitelist, user_id)) is not None

    async def add_to_whitelist(self, user_id: int):
        user = Whitelist(user_id=user_id)
        self.s.add(user)
        await self.s.commit()

    async def remove_from_whitelist(self, user_id: int):
        user = await self.s.get(Whitelist, user_id)
        if user:
            await self.s.delete(user)
            await self.s.commit()

    async def update_busy(self, user_id: int, busy: bool):
        await self.s.execute(update(User).where(User.id == user_id).values(busy=busy))
        await self.s.commit()
