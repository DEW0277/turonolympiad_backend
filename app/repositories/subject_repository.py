"""Subject repository for database operations.

This module provides the SubjectRepository class for managing subject data persistence,
implementing all database operations for the Subject model.
"""

from typing import Optional, Tuple, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subject import Subject
from app.repositories.base import BaseRepository


class SubjectRepository(BaseRepository[Subject]):
    """Repository for Subject model database operations.
    
    Handles all database operations for subject records including creation,
    retrieval, updates, and deletion. Uses async database operations
    for optimal performance.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize SubjectRepository with database session.
        
        Args:
            db: Async database session for operations
        """
        super().__init__(Subject, db)
    
    async def create(self, name: str) -> Subject:
        """Create a new subject record.
        
        Args:
            name: Subject name (must be unique)
            
        Returns:
            Created Subject instance with all fields populated
            
        Raises:
            IntegrityError: If name already exists in database
        """
        return await super().create(name=name)
    
    async def get_by_id(self, id: int) -> Optional[Subject]:
        """Retrieve subject by ID.
        
        Args:
            id: Subject's primary key ID
            
        Returns:
            Subject instance if found, None otherwise
        """
        return await super().get_by_id(id)
    
    async def get_by_name(self, name: str) -> Optional[Subject]:
        """Retrieve subject by name.
        
        Args:
            name: Subject name to search for
            
        Returns:
            Subject instance if found, None otherwise
        """
        result = await self.db.execute(
            select(Subject).where(Subject.name == name)
        )
        return result.scalar_one_or_none()
    
    async def list(self, skip: int = 0, limit: int = 50) -> Tuple[List[Subject], int]:
        """Fetch paginated subjects.
        
        Retrieves a paginated list of subjects ordered by created_at descending.
        
        Args:
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 50)
            
        Returns:
            Tuple of (subjects, total_count) where subjects is a list of Subject instances
            and total_count is the total number of subjects in database
        """
        # Get total count
        count_result = await self.db.execute(select(func.count(Subject.id)))
        total_count = count_result.scalar() or 0
        
        # Get paginated results
        result = await self.db.execute(
            select(Subject)
            .order_by(Subject.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        subjects = list(result.scalars().all())
        
        return (subjects, total_count)
    
    async def update(self, id: int, name: str) -> Subject:
        """Update subject by ID.
        
        Args:
            id: Subject's primary key ID
            name: New subject name
            
        Returns:
            Updated Subject instance
            
        Raises:
            ValueError: If subject with given ID does not exist
        """
        subject = await self.get_by_id(id)
        if subject is None:
            raise ValueError(f"Subject with id {id} not found")
        
        return await super().update(subject, name=name)
    
    async def delete(self, id: int) -> None:
        """Delete subject by ID.
        
        Args:
            id: Subject's primary key ID
            
        Raises:
            ValueError: If subject with given ID does not exist
        """
        subject = await self.get_by_id(id)
        if subject is None:
            raise ValueError(f"Subject with id {id} not found")
        
        await super().delete(subject)
