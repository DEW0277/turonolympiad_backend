from app.modules.auth.models.orm import User
from sqlalchemy import select, func


class AuthRepository:
    def __init__(self, db):
        self.db = db


    async def get_user_by_phone(self, phone_number: str):
        query = await self.db.execute(
            select(User).where(User.phone_number == phone_number)
        )
        return query.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int):
        query = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return query.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str):
        query = await self.db.execute(
            select(User).where(User.email == email)
        )
        return query.scalar_one_or_none()
    
    
    async def delete_user(self, user_id: int):
        query = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = query.scalar_one_or_none()
        if user:
            await self.db.delete(user)
            await self.db.commit()
            return True
        return False
    
    
    async def filter_users(self, **filters):
        query = select(User)
        for attr, value in filters.items():
            query = query.where(getattr(User, attr) == value)
        return await self.db.execute(query)


    async def get_paginated_filters(self, skip: int = 0, limit: int = 10, **filters):
        query = select(User)
        for attr, value in filters.items():
            query = query.where(getattr(User, attr) == value)
        total_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(total_query)).scalar()
        results = (await self.db.execute(query.offset(skip).limit(limit))).scalars().all()
        return {"total": total, "items": results}
    
    
    async def create_user(self, phone_number: str, hashed_password: str, first_name: str, last_name: str):
        new_user = User(phone_number=phone_number, hashed_password=hashed_password, first_name=first_name, last_name=last_name)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    