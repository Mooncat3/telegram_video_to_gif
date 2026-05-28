from __future__ import annotations

from sqlalchemy import BigInteger, Integer, String, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    processed_count: Mapped[int] = mapped_column(Integer, default=0)
    nickname: Mapped[str | None] = mapped_column(String(128))
    username: Mapped[str | None] = mapped_column(String(64))
    lang: Mapped[str] = mapped_column(String(8), default="en")
    file_limit_mb: Mapped[int] = mapped_column(Integer, default=10)
    busy: Mapped[bool] = mapped_column(Boolean, default=False)


class GlobalStats(Base):
    __tablename__ = "global_stats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    total_conversions: Mapped[int] = mapped_column(Integer, default=0)


class Admin(Base):
    __tablename__ = "admins"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)


class Whitelist(Base):
    __tablename__ = "whitelist"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
