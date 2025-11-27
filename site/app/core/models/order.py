from typing import Annotated
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, ForeignKey, Text, DateTime, func, Integer

from .base import BaseModel



order_date_type = Annotated[datetime, mapped_column(DateTime, server_default=func.now(), nullable=False)]
money = Annotated[float, mapped_column(Numeric(10, 2), nullable=False)]


class Order(BaseModel):
    """Модель Замовлення."""
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    order_date: Mapped[order_date_type]
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    total_amount: Mapped[money]
    shipping_address: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")

    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, status='{self.status}')>"