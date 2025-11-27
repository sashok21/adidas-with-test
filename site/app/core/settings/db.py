from typing import AsyncGenerator


from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError




class Database:
   def __init__(self, url: str):
       self.url = url


       self.engine = None
       self.session_maker = None


   async def connect(self):
       self.engine = create_async_engine(self.url, echo=False, pool_pre_ping=True)
       self.session_maker = async_sessionmaker(
           bind=self.engine,
           autoflush=False,
           expire_on_commit=False,
           class_=AsyncSession,
       )


   async def disconnect(self):
       if self.engine:
           await self.engine.dispose()
           self.engine = None
           self.session_maker = None


   async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
       if not self.session_maker:
           raise RuntimeError("Database not connected. Call connect() first.")
       async with self.session_maker() as session:
           yield session


   async def ping(self) -> bool:
       if not self.engine:
           raise RuntimeError("Database not connected. Call connect() first.")
       try:
           async with self.engine.begin() as conn:
               await conn.execute(text("SELECT 1"))
           return True
       except SQLAlchemyError:
           return False

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

db = Database(url=DATABASE_URL)