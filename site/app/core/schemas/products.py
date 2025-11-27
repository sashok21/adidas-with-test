from typing import Optional
from pydantic import BaseModel, Field, field_validator

# --- Вкладені схеми для відображення повних даних ---
class CategorySchema(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class BrandSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    class Config:
        from_attributes = True

# 1. Create
class ProductCreateSchema(BaseModel):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    price: float = Field(gt=0) # Ціна більше 0

    category_id: int = Field(gt=0)
    brand_id: int = Field(gt=0)
    in_stock: bool = Field(default=True)

    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        return round(float(v), 2)

    class Config:
        from_attributes = True

# 2. Read (Response)
class ProductResponseSchema(BaseModel):
    id: int = Field(gt=0)
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool
    # Замість просто ID повертаємо повні об'єкти
    category: CategorySchema
    brand: BrandSchema

    class Config:
        from_attributes = True

# 3. Update (PATCH)
class ProductPartialUpdateSchema(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    price: Optional[float] = Field(default=None, gt=0)
    in_stock: Optional[bool] = Field(default=None)
    category_id: Optional[int] = Field(default=None, gt=0)
    brand_id: Optional[int] = Field(default=None, gt=0)

    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v is not None:
            return round(float(v), 2)
        return v

    class Config:
        from_attributes = True


class BrandSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ProductResponseSchema(BaseModel):
    """Схема для повернення одного товару (повний набір полів)."""
    id: int = Field(gt=0)
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool
    category: CategorySchema
    brand: BrandSchema

    class Config:
        from_attributes = True


class ProductPartialUpdateSchema(BaseModel):
    """Схема для часткового оновлення товару (використовується PATCH)."""
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    price: Optional[float] = Field(default=None, gt=0)
    in_stock: Optional[bool] = Field(default=None)

    category_id: Optional[int] = Field(default=None, gt=0)
    brand_id: Optional[int] = Field(default=None, gt=0)

    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v is not None:
            return round(float(v), 2)
        return v

    class Config:
        from_attributes = True