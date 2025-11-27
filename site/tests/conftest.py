from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.models import BaseModel
from main import app
from app.core.settings.db import db
from tests.factories import CategoryFactory, BrandFactory, ProductFactory, UserFactory

# Використовуємо базу даних у пам'яті для тестів
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


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
async def client(db_session, monkeypatch) -> AsyncGenerator[AsyncClient, Any]:
    async def override_get_session():
        yield db_session

    app.dependency_overrides[db.get_session] = override_get_session

    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client


# --- ДОДАНО: Реєстрація фабрик як асинхронних фікстур ---

@pytest.fixture
def category_factory(db_session):
    async def factory(**kwargs):
        # Створюємо об'єкт (build), але не зберігаємо через синхронну сесію фабрики
        category = CategoryFactory.build(**kwargs)
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        return category

    return factory


@pytest.fixture
def brand_factory(db_session):
    async def factory(**kwargs):
        brand = BrandFactory.build(**kwargs)
        db_session.add(brand)
        await db_session.commit()
        await db_session.refresh(brand)
        return brand

    return factory


@pytest.fixture
def user_factory(db_session):
    async def factory(**kwargs):
        user = UserFactory.build(**kwargs)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return factory


@pytest.fixture
def product_factory(db_session, category_factory, brand_factory):
    async def factory(**kwargs):
        # Якщо категорія або бренд не передані, створюємо їх
        if "category" not in kwargs:
            kwargs["category"] = await category_factory()
        if "brand" not in kwargs:
            kwargs["brand"] = await brand_factory()

        product = ProductFactory.build(**kwargs)
        # Явно прив'язуємо ID (важливо для асинхронної сесії)
        product.category_id = kwargs["category"].id
        product.brand_id = kwargs["brand"].id

        db_session.add(product)
        await db_session.commit()
        await db_session.refresh(product)
        return product

    return factory