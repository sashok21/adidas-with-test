from typing import Optional
from pydantic import BaseModel, Field

# --- Вкладена схема ---
class ProductBrandNestedSchema(BaseModel):
    id: int = Field(gt=0)
    name: str
    price: float

    class Config:
        from_attributes = True

# 1. Create
class BrandCreateSchema(BaseModel):
    name: str = Field(max_length=50)
    description: Optional[str] = None

    class Config:
        from_attributes = True

# 2. Read (Response)
class BrandResponseSchema(BrandCreateSchema):
    id: int = Field(gt=0)
    products: list[ProductBrandNestedSchema] = []

    class Config:
        from_attributes = True

# 3. Update (PATCH)
class BrandPartialUpdateSchema(BaseModel):
    name: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None)

    class Config:
        from_attributes = True