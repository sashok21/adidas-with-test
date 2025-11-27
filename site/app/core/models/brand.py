from typing import Optional

from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String, Integer

from .base import BaseModel


class Brand(BaseModel):
    """Модель Бренду (Виробника) кросівок."""
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    products: Mapped[list["Product"]] = relationship(back_populates="brand")