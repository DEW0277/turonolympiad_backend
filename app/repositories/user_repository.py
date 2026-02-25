"""User repository for database operations.

This module provides the UserRepository class for managing user data persistence,
implementing all database operations for the User model.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model database operations.
    
    Handles all database operations for user records including creation,
    retrieval, updates, and existence checks. Uses async database operations
    for optimal performance.
    
    Requirements:
        - 11.1: Repository handles all database operations for user data
        - 11.2: Repository provides methods for creating, reading, updating user records
        - 11.3: Repository uses asynchronous database operations
        - 11.5: Repository does not contain business logic
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize UserRepository with database session.
        
        Args:
            db: Async database session for operations
        """
        super().__init__(User, db)
    
    async def create(
        self, 
        email: str, 
        hashed_password: str, 
        is_verified: bool = False
    ) -> User:
        """Create a new user record.
        
        Args:
            email: User's email address (must be unique)
            hashed_password: Bcrypt hash of user's password
            is_verified: Whether user has verified their email (default: False)
            
        Returns:
            Created User instance with all fields populated
            
        Raises:
            IntegrityError: If email already exists in database
        """
        return await super().create(
            email=email,
            hashed_password=hashed_password,
            is_verified=is_verified
        )
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User instance if found, None otherwise
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve user by ID.
        
        Args:
            user_id: User's primary key ID
            
        Returns:
            User instance if found, None otherwise
        """
        return await super().get_by_id(user_id)
    
    async def update_verification_status(
        self, 
        user_id: int, 
        is_verified: bool
    ) -> User:
        """Update user's email verification status.
        
        Args:
            user_id: User's primary key ID
            is_verified: New verification status (True for verified, False for pending)
            
        Returns:
            Updated User instance
            
        Raises:
            ValueError: If user with given ID does not exist
        """
        user = await self.get_by_id(user_id)
        if user is None:
            raise ValueError(f"User with id {user_id} not found")
        
        return await super().update(user, is_verified=is_verified)
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if user with given email exists.
        
        Args:
            email: Email address to check
            
        Returns:
            True if user with email exists, False otherwise
        """
        return await super().exists(email=email)
