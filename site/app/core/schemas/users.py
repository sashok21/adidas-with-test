from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


# Вкладена схема
class OrderUserNestedSchema(BaseModel):
    id: int
    order_date: datetime
    status: str
    total_amount: float

    class Config:
        from_attributes = True


# 1. Create
class UserCreateSchema(BaseModel):
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=8, max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    phone_number: Optional[str] = Field(default=None, max_length=20)

    class Config:
        from_attributes = True


# 2. Read (Response)
class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]

    # Пароль виключаємо (exclude=True у коді роутера або просто не додаємо сюди)
    orders: List[OrderUserNestedSchema] = []

    class Config:
        from_attributes = True


# 3. Update (PATCH)
class UserPartialUpdateSchema(BaseModel):
    email: Optional[EmailStr] = Field(default=None, max_length=100)
    password: Optional[str] = Field(default=None, min_length=8, max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    phone_number: Optional[str] = Field(default=None, max_length=20)

    class Config:
        from_attributes = True