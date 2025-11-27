import pytest
from app.core.schemas.products import ProductResponseSchema


@pytest.fixture()
def category_payload(faker):
    return {"name": faker.word()}


@pytest.mark.asyncio
async def test_create_category(client, category_payload):
    response = await client.post("/categories/", json=category_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == category_payload["name"]
    assert "id" in data


@pytest.mark.asyncio
async def test_get_category(client, category_factory):
    category = await category_factory()
    response = await client.get(f"/categories/{category.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category.id
    assert data["name"] == category.name


@pytest.mark.asyncio
async def test_get_categories(client, category_factory):
    # Створюємо 3 категорії
    [await category_factory() for _ in range(3)]
    response = await client.get("/categories/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


@pytest.mark.asyncio
async def test_partial_update_category(client, category_factory):
    category = await category_factory()
    payload = {"name": "Updated Category Name"}
    response = await client.patch(f"/categories/{category.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]


@pytest.mark.asyncio
async def test_delete_category(client, category_factory):
    category = await category_factory()
    response = await client.delete(f"/categories/{category.id}")
    assert response.status_code == 204
    # Перевіряємо, що дійсно видалили
    get_response = await client.get(f"/categories/{category.id}")
    assert get_response.status_code == 404


# -----------------------------------------------------------------------------
#                                  BRANDS
# -----------------------------------------------------------------------------

@pytest.fixture()
def brand_payload(faker):
    return {
        "name": faker.company(),
        "description": faker.sentence()
    }


@pytest.mark.asyncio
async def test_create_brand(client, brand_payload):
    response = await client.post("/brands/", json=brand_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == brand_payload["name"]


@pytest.mark.asyncio
async def test_get_brand(client, brand_factory):
    brand = await brand_factory()
    response = await client.get(f"/brands/{brand.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == brand.id


@pytest.mark.asyncio
async def test_update_brand_partial(client, brand_factory):
    brand = await brand_factory()
    payload = {"name": "Nike Updated"}
    response = await client.patch(f"/brands/{brand.id}", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Nike Updated"


@pytest.mark.asyncio
async def test_delete_brand(client, brand_factory):
    brand = await brand_factory()
    response = await client.delete(f"/brands/{brand.id}")
    assert response.status_code == 204


# -----------------------------------------------------------------------------
#                                   USERS
# -----------------------------------------------------------------------------

@pytest.fixture()
def user_payload(faker):
    return {
        "email": faker.email(),
        "password": "securepassword",
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "phone_number": "1234567890"
    }


@pytest.mark.asyncio
async def test_create_user(client, user_payload):
    response = await client.post("/users/", json=user_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_payload["email"]
    assert "password" not in data  # Пароль не повинен повертатися


@pytest.mark.asyncio
async def test_get_user(client, user_factory):
    user = await user_factory()
    response = await client.get(f"/users/{user.id}")
    assert response.status_code == 200
    assert response.json()["email"] == user.email


@pytest.mark.asyncio
async def test_update_user_put(client, user_factory, faker):
    user = await user_factory()
    # PUT вимагає всі поля
    updated_payload = {
        "email": "newemail@example.com",
        "password": "newpassword",
        "first_name": "NewName",
        "last_name": "NewLast",
        "phone_number": "0987654321"
    }
    response = await client.put(f"/users/{user.id}", json=updated_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == updated_payload["email"]
    assert data["first_name"] == updated_payload["first_name"]


@pytest.mark.asyncio
async def test_delete_user(client, user_factory):
    user = await user_factory()
    response = await client.delete(f"/users/{user.id}")
    assert response.status_code == 204


# -----------------------------------------------------------------------------
#                                 PRODUCTS
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_product(client, category_factory, brand_factory, faker):
    # Спочатку створюємо залежності
    category = await category_factory()
    brand = await brand_factory()

    payload = {
        "name": faker.word(),
        "description": faker.sentence(),
        "price": 100.50,
        "category_id": category.id,
        "brand_id": brand.id,
        "in_stock": True
    }

    response = await client.post("/products/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["category"]["id"] == category.id
    assert data["brand"]["id"] == brand.id


@pytest.mark.asyncio
async def test_get_product(client, product_factory):
    product = await product_factory()
    response = await client.get(f"/products/{product.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product.id
    assert data["price"] == product.price


@pytest.mark.asyncio
async def test_update_product_patch(client, product_factory):
    product = await product_factory()
    payload = {"price": 500.00, "in_stock": False}

    response = await client.patch(f"/products/{product.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 500.00
    assert data["in_stock"] is False


@pytest.mark.asyncio
async def test_delete_product(client, product_factory):
    product = await product_factory()
    response = await client.delete(f"/products/{product.id}")
    assert response.status_code == 204


# -----------------------------------------------------------------------------
#                                  ORDERS
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_order(client, user_factory):
    user = await user_factory()
    payload = {
        "user_id": user.id,
        "status": "new",
        "shipping_address": "Kyiv, Street 1"
    }

    response = await client.post("/orders/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "new"
    assert data["total_amount"] == 0.0  # Початкова сума


@pytest.mark.asyncio
async def test_get_orders(client, user_factory):
    user = await user_factory()
    # Створюємо замовлення через API, оскільки фабрики Order у нас немає
    await client.post("/orders/", json={"user_id": user.id, "status": "new"})

    response = await client.get("/orders/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_patch_order(client, user_factory):
    user = await user_factory()
    # Створюємо
    create_resp = await client.post("/orders/", json={"user_id": user.id, "status": "new"})
    order_id = create_resp.json()["id"]

    # Оновлюємо
    response = await client.patch(f"/orders/{order_id}", json={"status": "shipped"})
    assert response.status_code == 200
    assert response.json()["status"] == "shipped"


@pytest.mark.asyncio
async def test_delete_order(client, user_factory):
    user = await user_factory()
    create_resp = await client.post("/orders/", json={"user_id": user.id, "status": "new"})
    order_id = create_resp.json()["id"]

    response = await client.delete(f"/orders/{order_id}")
    assert response.status_code == 204


# -----------------------------------------------------------------------------
#                               ORDER ITEMS
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_order_item(client, user_factory, product_factory):
    # Підготовка даних
    user = await user_factory()
    product = await product_factory()

    # Створюємо замовлення
    order_resp = await client.post("/orders/", json={"user_id": user.id, "status": "new"})
    order_id = order_resp.json()["id"]

    # Додаємо товар у замовлення
    payload = {
        "order_id": order_id,
        "product_id": product.id,
        "quantity": 2
    }

    response = await client.post("/order_items/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["quantity"] == 2
    # Перевіряємо, що ціна підтягнулась з товару
    assert data["unit_price"] == product.price


@pytest.mark.asyncio
async def test_update_order_item_quantity(client, user_factory, product_factory):
    # Підготовка
    user = await user_factory()
    product = await product_factory()
    order_resp = await client.post("/orders/", json={"user_id": user.id, "status": "new"})
    order_id = order_resp.json()["id"]

    item_resp = await client.post("/order_items/", json={
        "order_id": order_id, "product_id": product.id, "quantity": 1
    })
    item_id = item_resp.json()["id"]

    # Тест оновлення (PATCH)
    response = await client.patch(f"/order_items/{item_id}", json={"quantity": 5})
    assert response.status_code == 200
    assert response.json()["quantity"] == 5


@pytest.mark.asyncio
async def test_delete_order_item(client, user_factory, product_factory):
    # Підготовка
    user = await user_factory()
    product = await product_factory()
    order_resp = await client.post("/orders/", json={"user_id": user.id, "status": "new"})
    order_id = order_resp.json()["id"]

    item_resp = await client.post("/order_items/", json={
        "order_id": order_id, "product_id": product.id, "quantity": 1
    })
    item_id = item_resp.json()["id"]

    # Видалення
    response = await client.delete(f"/order_items/{item_id}")
    assert response.status_code == 204