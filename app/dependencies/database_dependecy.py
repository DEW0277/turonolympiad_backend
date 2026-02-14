from app.database.base import Base
from app.database.session import SessionLocal


async def get_session():
    async with SessionLocal() as session:
        yield session