from typing import Optional
from pydantic import BaseModel, Field

# Вкладені схеми
class OrderItemOrderNestedSchema(BaseModel):
    id: int
    status: str
    total_amount: float
    class Config:
        from_attributes = True

class OrderItemProductNestedSchema(BaseModel):
    id: int
    name: str
    price: float
    class Config:
        from_attributes = True

# 1. Create
class OrderItemCreateSchema(BaseModel):
    order_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0)

    class Config:
        from_attributes = True

# 2. Read (Response)
class OrderItemResponseSchema(OrderItemCreateSchema):
    id: int = Field(gt=0)
    unit_price: float

    order: OrderItemOrderNestedSchema
    product: OrderItemProductNestedSchema

    order_id: int = Field(exclude=True)
    product_id: int = Field(exclude=True)

    class Config:
        from_attributes = True

# 3. Update (PATCH)
class OrderItemPartialUpdateSchema(BaseModel):
    quantity: Optional[int] = Field(default=None, gt=0)

    class Config:
        from_attributes = True

