from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.brand import Brand
from app.core.schemas.brands import (
    BrandResponseSchema,
    BrandCreateSchema,
    BrandPartialUpdateSchema
)
from app.core.settings.db import db

SessionDepend = Annotated[AsyncSession, Depends(db.get_session)]
router = APIRouter(prefix="/brands", tags=["Brands"])


@router.get("/", response_model=List[BrandResponseSchema])
async def get_brands(session: SessionDepend):
    query = select(Brand).options(selectinload(Brand.products))
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/{brand_id}", response_model=BrandResponseSchema)
async def get_brand(brand_id: int, session: SessionDepend):
    query = select(Brand).filter(Brand.id == brand_id).options(selectinload(Brand.products))
    result = await session.execute(query)
    brand = result.scalars().first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.post("/", response_model=BrandResponseSchema, status_code=201)
async def create_brand(brand: BrandCreateSchema, session: SessionDepend):
    new_brand = Brand(**brand.model_dump())
    session.add(new_brand)
    try:
        await session.commit()

        # Надійно завантажуємо
        query = select(Brand).filter(Brand.id == new_brand.id).options(selectinload(Brand.products))
        result = await session.execute(query)
        created_brand = result.scalars().first()

        return created_brand
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{brand_id}", response_model=BrandResponseSchema)
async def partial_update_brand(brand_id: int, brand: BrandPartialUpdateSchema, session: SessionDepend):
    query = select(Brand).filter(Brand.id == brand_id).options(selectinload(Brand.products))
    result = await session.execute(query)
    existing_brand = result.scalars().first()
    if not existing_brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    for key, value in brand.model_dump(exclude_unset=True).items():
        setattr(existing_brand, key, value)

    await session.commit()
    return existing_brand


@router.delete("/{brand_id}", status_code=204)
async def delete_brand(brand_id: int, session: SessionDepend):
    existing_brand = await session.get(Brand, brand_id)
    if not existing_brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    await session.delete(existing_brand)
    await session.commit()
    return None