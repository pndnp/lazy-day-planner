import datetime
import json
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from bot.db import engine


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    settings_json: Mapped[str] = mapped_column(String, default="{}")

    events: Mapped[list["Event"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def settings(self) -> dict[str, Any]:
        try:
            parsed: dict[str, Any] = json.loads(self.settings_json or "{}")
            return parsed
        except json.JSONDecodeError:
            return {}

    @settings.setter
    def settings(self, value: dict[str, Any]) -> None:
        self.settings_json = json.dumps(value, ensure_ascii=False)

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        s = self.settings
        s[key] = value
        self.settings = s

    def toggle_setting(self, key: str, default: bool = False) -> bool:
        s = self.settings
        new_val = not s.get(key, default)
        s[key] = new_val
        self.settings = s
        return new_val


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    date_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="events")


async def create_tables() -> None:
    """Create database tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
