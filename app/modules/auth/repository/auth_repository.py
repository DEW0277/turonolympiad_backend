from app.modules.auth.models.orm import User, UserRole
from sqlalchemy import select, func
from typing import List, Optional


class AuthRepository:
    def __init__(self, db):
        self.db = db


    async def get_user_by_phone(self, phone_number: str):
        query = await self.db.execute(
            select(User).where(User.phone_number == phone_number)
        )
        return query.scalar_one_or_none()

    async def get_user_by_id(self, user_id: str):
        query = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return query.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str):
        query = await self.db.execute(
            select(User).where(User.email == email)
        )
        return query.scalar_one_or_none()
    
    
    async def delete_user(self, user_id: str):
        user = await self.get_user_by_id(user_id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
            return True
        return False
    
    
    async def filter_users(self, **filters):
        query = select(User)
        for attr, value in filters.items():
            if hasattr(User, attr):
                query = query.where(getattr(User, attr) == value)
        return await self.db.execute(query)


    async def get_paginated_filters(self, skip: int = 0, limit: int = 10, **filters):
        query = select(User)
        for attr, value in filters.items():
            if hasattr(User, attr):
                query = query.where(getattr(User, attr) == value)
        total_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(total_query)).scalar()
        results = (await self.db.execute(query.offset(skip).limit(limit))).scalars().all()
        return {"total": total, "items": results}
    
    
    async def create_user(self, phone_number: str, hashed_password: str, first_name: str, last_name: str, role: UserRole = UserRole.ORDINARY):
        new_user = User(
            phone_number=phone_number,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    
    async def update_user_role(self, user_id: str, role: UserRole):
        """Update user's role (admin only)"""
        user = await self.get_user_by_id(user_id)
        if user:
            user.role = role
            await self.db.commit()
            await self.db.refresh(user)
            return user
        return None

    
    async def update_user_status(self, user_id: str, is_active: bool):
        """Activate or deactivate user (admin only)"""
        user = await self.get_user_by_id(user_id)
        if user:
            user.is_active = is_active
            await self.db.commit()
            await self.db.refresh(user)
            return user
        return None

    
    async def get_all_users(self, skip: int = 0, limit: int = 100):
        """Get all users with pagination (admin only)"""
        query = select(User)
        total_query = select(func.count(User.id))
        
        total = (await self.db.execute(total_query)).scalar()
        results = (await self.db.execute(query.offset(skip).limit(limit))).scalars().all()
        
        return {"total": total, "items": results}

    
    async def get_admins(self):
        """Get all admin users"""
        query = await self.db.execute(
            select(User).where(User.role == UserRole.ADMIN)
        )
        return query.scalars().all()

    
    async def get_admin_count(self):
        """Get count of admin users"""
        query = await self.db.execute(
            select(func.count(User.id)).where(User.role == UserRole.ADMIN)
        )
        return query.scalar() or 0