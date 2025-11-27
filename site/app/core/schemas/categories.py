from typing import Optional
from pydantic import BaseModel, Field

# --- Вкладений клас для відображення продуктів у категорії ---
class ProductCategoryNestedSchema(BaseModel):
    id: int = Field(gt=0)
    name: str
    price: float

    class Config:
        from_attributes = True

# 1. Схема для СТВОРЕННЯ (Create)
class CategoryCreateSchema(BaseModel):
    """Схема для створення нової Категорії."""
    # Обмеження довжини, як в прикладі практичної
    name: str = Field(max_length=50)

    class Config:
        from_attributes = True

# 2. Схема для ВІДПОВІДІ (Read)
class CategoryResponseSchema(CategoryCreateSchema):
    """Схема для повернення Категорії з БД."""
    id: int = Field(gt=0)
    # Повертаємо список продуктів разом з категорією
    products: list[ProductCategoryNestedSchema] = []

    class Config:
        from_attributes = True

# 3. Схема для ЧАСТКОВОГО ОНОВЛЕННЯ (Update/PATCH)
class CategoryPartialUpdateSchema(BaseModel):
    """Схема для часткового оновлення. Всі поля Optional."""
    name: Optional[str] = Field(default=None, max_length=50)

    class Config:
        from_attributes = True