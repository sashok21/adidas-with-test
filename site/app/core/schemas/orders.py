from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# Вкладені схеми
class UserOrderNestedSchema(BaseModel):
    id: int
    email: str
    first_name: Optional[str] = None

    class Config:
        from_attributes = True


class OrderItemOrderNestedSchema(BaseModel):
    id: int
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: float

    class Config:
        from_attributes = True


# 1. Create
class OrderCreateSchema(BaseModel):
    user_id: int = Field(gt=0)
    status: str = Field(max_length=20)
    shipping_address: Optional[str] = None

    class Config:
        from_attributes = True


# 2. Read (Response)
class OrderResponseSchema(OrderCreateSchema):
    id: int = Field(gt=0)
    order_date: datetime
    total_amount: float

    user: UserOrderNestedSchema
    items: List[OrderItemOrderNestedSchema] = []

    # Виключаємо user_id, бо повертаємо повний об'єкт user
    user_id: int = Field(exclude=True)

    class Config:
        from_attributes = True


# 3. Update (PATCH)
class OrderPartialUpdateSchema(BaseModel):
    status: Optional[str] = Field(default=None, max_length=20)
    shipping_address: Optional[str] = Field(default=None)

    class Config:
        from_attributes = True