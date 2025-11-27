from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer

from .base import BaseModel


class User(BaseModel):
    """Модель Користувача/Клієнта."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    phone_number: Mapped[str | None] = mapped_column(String(20))

    orders: Mapped[list["Order"]] = relationship(back_populates="user")

