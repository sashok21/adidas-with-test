from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.category import Category
from app.core.schemas.categories import (
    CategoryResponseSchema,
    CategoryCreateSchema,
    CategoryPartialUpdateSchema
)
from app.core.settings.db import db

SessionDepend = Annotated[AsyncSession, Depends(db.get_session)]
router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryResponseSchema])
async def get_categories(session: SessionDepend):
    query = select(Category).options(selectinload(Category.products))
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/{category_id}", response_model=CategoryResponseSchema)
async def get_category(category_id: int, session: SessionDepend):
    query = select(Category).filter(Category.id == category_id).options(selectinload(Category.products))
    result = await session.execute(query)
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=CategoryResponseSchema, status_code=201)
async def create_category(category: CategoryCreateSchema, session: SessionDepend):
    new_category = Category(**category.model_dump())
    session.add(new_category)
    try:
        await session.commit()

        # Надійно завантажуємо створену категорію
        query = select(Category).filter(Category.id == new_category.id).options(selectinload(Category.products))
        result = await session.execute(query)
        created_category = result.scalars().first()

        return created_category
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{category_id}", response_model=CategoryResponseSchema)
async def partial_update_category(category_id: int, category: CategoryPartialUpdateSchema, session: SessionDepend):
    query = select(Category).filter(Category.id == category_id).options(selectinload(Category.products))
    result = await session.execute(query)
    existing_category = result.scalars().first()
    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found")

    for key, value in category.model_dump(exclude_unset=True).items():
        setattr(existing_category, key, value)

    await session.commit()
    return existing_category


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int, session: SessionDepend):
    existing_category = await session.get(Category, category_id)
    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found")
    await session.delete(existing_category)
    await session.commit()
    return None