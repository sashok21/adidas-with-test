from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.core.schemas.users import (
    UserResponseSchema,
    UserCreateSchema,
    UserPartialUpdateSchema
)
from app.core.settings.db import db

SessionDepend = Annotated[AsyncSession, Depends(db.get_session)]

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponseSchema])
async def get_users(session: SessionDepend):
    query = select(User).options(selectinload(User.orders))
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserResponseSchema)
async def get_user(user_id: int, session: SessionDepend):
    query = select(User).filter(User.id == user_id).options(selectinload(User.orders))
    result = await session.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponseSchema, status_code=201)
async def create_user(user: UserCreateSchema, session: SessionDepend):
    # 1. Створюємо
    new_user = User(**user.model_dump())
    session.add(new_user)
    try:
        await session.commit()

        # 2. НАДІЙНИЙ СПОСІБ: Завантажуємо створений об'єкт разом зі зв'язками
        query = select(User).filter(User.id == new_user.id).options(selectinload(User.orders))
        result = await session.execute(query)
        created_user = result.scalars().first()

        return created_user
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}", response_model=UserResponseSchema)
async def update_user(user_id: int, user: UserCreateSchema, session: SessionDepend):
    query = select(User).filter(User.id == user_id).options(selectinload(User.orders))
    result = await session.execute(query)
    existing_user = result.scalars().first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user.model_dump().items():
        setattr(existing_user, key, value)

    await session.commit()
    # Тут об'єкт вже завантажений, refresh спрацює, але для надійності можна повернути existing_user
    return existing_user


@router.patch("/{user_id}", response_model=UserResponseSchema)
async def partial_update_user(user_id: int, user: UserPartialUpdateSchema, session: SessionDepend):
    query = select(User).filter(User.id == user_id).options(selectinload(User.orders))
    result = await session.execute(query)
    existing_user = result.scalars().first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user.model_dump(exclude_unset=True).items():
        setattr(existing_user, key, value)

    await session.commit()
    return existing_user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, session: SessionDepend):
    existing_user = await session.get(User, user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    await session.delete(existing_user)
    await session.commit()
    return None