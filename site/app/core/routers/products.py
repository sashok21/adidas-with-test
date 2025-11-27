from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.core.models.product import Product
from app.core.schemas.products import (
    ProductResponseSchema,
    ProductCreateSchema,
    ProductPartialUpdateSchema
)
from app.core.settings.db import db

SessionDepend = Annotated[AsyncSession, Depends(db.get_session)]

router = APIRouter(prefix="/products", tags=["Products"])


# --- GET (Список товарів) ---
@router.get(
    path="/",
    response_model=List[ProductResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_products(session: SessionDepend):
    """Отримати список всіх товарів (з категоріями та брендами)."""
    query = select(Product).options(
        selectinload(Product.category),
        selectinload(Product.brand)
    )
    result = await session.execute(query)
    return result.scalars().all()


# --- GET (Один товар) ---
@router.get(
    path="/{product_id}",
    response_model=ProductResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_product(product_id: int, session: SessionDepend):
    """Отримати один товар за ID."""
    query = select(Product).filter(Product.id == product_id).options(
        selectinload(Product.category),
        selectinload(Product.brand)
    )
    result = await session.execute(query)
    existing_product = result.scalars().first()

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id={product_id} not found."
        )
    return existing_product


# --- CREATE (Створення товару) - ВИПРАВЛЕНО ---
@router.post(
    path="/",
    response_model=ProductResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
        product: ProductCreateSchema,
        session: SessionDepend
):
    """Створити новий товар."""
    product_data = product.model_dump()
    new_product = Product(**product_data)

    session.add(new_product)

    try:
        await session.commit()

        # ВИПРАВЛЕННЯ: Замість refresh робимо select з підвантаженням зв'язків
        query = select(Product).filter(Product.id == new_product.id).options(
            selectinload(Product.category),
            selectinload(Product.brand)
        )
        result = await session.execute(query)
        created_product = result.scalars().first()

        return created_product
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating product: {e}"
        )


# --- UPDATE (Повне оновлення - PUT) ---
@router.put(
    path="/{product_id}",
    response_model=ProductResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_product(
        product_id: int,
        product: ProductCreateSchema,
        session: SessionDepend
):
    """Повністю оновити товар за ID."""
    # Спочатку завантажуємо товар
    query = select(Product).filter(Product.id == product_id).options(
        selectinload(Product.category),
        selectinload(Product.brand)
    )
    result = await session.execute(query)
    existing_product = result.scalars().first()

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id={product_id} not found."
        )

    # Оновлюємо поля
    update_data = product.model_dump()
    for field, value in update_data.items():
        setattr(existing_product, field, value)

    try:
        await session.commit()
        # Об'єкт вже завантажений з зв'язками, тому тут refresh безпечний,
        # або можна повернути existing_product так
        return existing_product
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating product: {e}"
        )


# --- PATCH (Часткове оновлення) ---
@router.patch(
    path="/{product_id}",
    response_model=ProductResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def partial_update_product(
        product_id: int,
        product: ProductPartialUpdateSchema,
        session: SessionDepend
):
    """Частково оновити товар (тільки передані поля)."""
    query = select(Product).filter(Product.id == product_id).options(
        selectinload(Product.category),
        selectinload(Product.brand)
    )
    result = await session.execute(query)
    existing_product = result.scalars().first()

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id={product_id} not found."
        )

    update_data = product.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(existing_product, field, value)

    try:
        await session.commit()
        return existing_product
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating product: {e}"
        )


# --- DELETE (Видалення) ---
@router.delete(
    path="/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(product_id: int, session: SessionDepend):
    """Видалити товар за ID."""
    existing_product = await session.get(Product, product_id)

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id={product_id} not found."
        )

    await session.delete(existing_product)
    await session.commit()

    return None