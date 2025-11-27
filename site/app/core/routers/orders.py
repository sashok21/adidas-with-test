from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.order import Order
from app.core.schemas.orders import (
    OrderResponseSchema,
    OrderCreateSchema,
    OrderPartialUpdateSchema
)
from app.core.settings.db import db

SessionDepend = Annotated[AsyncSession, Depends(db.get_session)]
router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", response_model=List[OrderResponseSchema])
async def get_orders(session: SessionDepend):
    query = select(Order).options(selectinload(Order.user), selectinload(Order.items))
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/{order_id}", response_model=OrderResponseSchema)
async def get_order(order_id: int, session: SessionDepend):
    query = select(Order).filter(Order.id == order_id).options(selectinload(Order.user), selectinload(Order.items))
    result = await session.execute(query)
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/", response_model=OrderResponseSchema, status_code=201)
async def create_order(order: OrderCreateSchema, session: SessionDepend):
    new_order = Order(**order.model_dump(), total_amount=0.0)
    session.add(new_order)
    try:
        await session.commit()

        # Надійно завантажуємо User та Items
        query = select(Order).filter(Order.id == new_order.id).options(selectinload(Order.user),
                                                                       selectinload(Order.items))
        result = await session.execute(query)
        created_order = result.scalars().first()

        return created_order
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{order_id}", response_model=OrderResponseSchema)
async def partial_update_order(order_id: int, order: OrderPartialUpdateSchema, session: SessionDepend):
    query = select(Order).filter(Order.id == order_id).options(selectinload(Order.user), selectinload(Order.items))
    result = await session.execute(query)
    existing_order = result.scalars().first()
    if not existing_order:
        raise HTTPException(status_code=404, detail="Order not found")

    for key, value in order.model_dump(exclude_unset=True).items():
        setattr(existing_order, key, value)

    await session.commit()
    return existing_order


@router.delete("/{order_id}", status_code=204)
async def delete_order(order_id: int, session: SessionDepend):
    existing_order = await session.get(Order, order_id)
    if not existing_order:
        raise HTTPException(status_code=404, detail="Order not found")
    await session.delete(existing_order)
    await session.commit()
    return None