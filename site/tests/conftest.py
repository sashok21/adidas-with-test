from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from faker import Faker

from app.core.models import BaseModel
from main import app
from app.core.settings.db import db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def faker():
    """Фікстура для Faker"""
    return Faker()


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def db_session(db_engine):
    async_session = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(loop_scope="function", autouse=True)
async def clear_db(db_session: AsyncSession):
    for table in reversed(BaseModel.metadata.sorted_tables):
        await db_session.execute(table.delete())
    await db_session.commit()


@pytest_asyncio.fixture(loop_scope="function")
async def client(db_session) -> AsyncGenerator[AsyncClient, Any]:
    async def override_get_session():
        yield db_session

    app.dependency_overrides[db.get_session] = override_get_session

    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client


# Фабрики як фікстури
@pytest.fixture
def category_factory(db_session, faker):
    async def factory(**kwargs):
        from app.core.models import Category

        category = Category(
            name=kwargs.get("name", faker.unique.word()),
            **{k: v for k, v in kwargs.items() if k != "name"}
        )
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        return category

    return factory


@pytest.fixture
def brand_factory(db_session, faker):
    async def factory(**kwargs):
        from app.core.models import Brand

        brand = Brand(
            name=kwargs.get("name", faker.unique.company()),
            description=kwargs.get("description", faker.sentence()),
            **{k: v for k, v in kwargs.items() if k not in ["name", "description"]}
        )
        db_session.add(brand)
        await db_session.commit()
        await db_session.refresh(brand)
        return brand

    return factory


@pytest.fixture
def user_factory(db_session, faker):
    async def factory(**kwargs):
        from app.core.models import User

        user = User(
            email=kwargs.get("email", faker.unique.email()),
            password=kwargs.get("password", "password123"),
            first_name=kwargs.get("first_name", faker.first_name()),
            last_name=kwargs.get("last_name", faker.last_name()),
            phone_number=kwargs.get("phone_number", faker.phone_number()),
            **{k: v for k, v in kwargs.items()
               if k not in ["email", "password", "first_name", "last_name", "phone_number"]}
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return factory


@pytest.fixture
def product_factory(db_session, category_factory, brand_factory, faker):
    async def factory(**kwargs):
        from app.core.models import Product

        # Створюємо категорію та бренд якщо не передані
        if "category_id" not in kwargs:
            category = await category_factory()
            kwargs["category_id"] = category.id

        if "brand_id" not in kwargs:
            brand = await brand_factory()
            kwargs["brand_id"] = brand.id

        product = Product(
            name=kwargs.get("name", faker.unique.word() + " " + faker.word()),
            description=kwargs.get("description", faker.sentence()),
            price=kwargs.get("price", float(faker.pydecimal(left_digits=3, right_digits=2, positive=True))),
            in_stock=kwargs.get("in_stock", True),
            category_id=kwargs["category_id"],
            brand_id=kwargs["brand_id"]
        )
        db_session.add(product)
        await db_session.commit()
        await db_session.refresh(product)
        return product

    return factory

