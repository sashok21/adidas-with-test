from typing import Union

from fastapi import FastAPI


from app.core.settings.db import DATABASE_URL, db
from contextlib import asynccontextmanager
from app.core.models.base import BaseModel


from app.core.routers import products, users, brands, categories, orders, order_items


@asynccontextmanager
async def lifespan(_fastapi_app: FastAPI):
   await db.connect()
   async with db.engine.begin() as connection:
       await connection.run_sync(BaseModel.metadata.create_all)
   yield
   await db.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(products.router)
app.include_router(users.router)
app.include_router(brands.router)
app.include_router(categories.router)
app.include_router(orders.router)
app.include_router(order_items.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get(path="/health", tags=["System"])
async def health():
   ok = await db.ping()
   return {"status": "ok" if ok else "error"}

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        app,
        port=8000,
        log_level="info",
        use_colors=False,
    )
