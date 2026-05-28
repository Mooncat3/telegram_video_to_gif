import asyncio

from config import settings
from db import engine, Base, Session
from db.models import Admin, Whitelist


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # seed admin ids from .env
    async with Session() as s:
        for aid in settings.admin_ids:
            if await s.get(Admin, aid) is None:
                s.add(Admin(user_id=aid))
            if await s.get(Whitelist, aid) is None:
                s.add(Whitelist(user_id=aid))
        await s.commit()

if __name__ == "__main__":
    asyncio.run(main())
