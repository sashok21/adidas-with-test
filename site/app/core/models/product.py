from typing import Optional
from sqlalchemy import Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel



class Product(BaseModel):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category: Mapped["Category"] = relationship(back_populates="products")

    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"), nullable=False)
    brand: Mapped["Brand"] = relationship(back_populates="products")

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")
