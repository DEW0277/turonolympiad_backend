"""Level repository for database operations.

This module provides the LevelRepository class for managing level data persistence,
implementing all database operations for the Level model.
"""

from typing import Optional, Tuple, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.level import Level
from app.repositories.base import BaseRepository


class LevelRepository(BaseRepository[Level]):
    """Repository for Level model database operations.
    
    Handles all database operations for level records including creation,
    retrieval, updates, and deletion. Uses async database operations
    for optimal performance.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize LevelRepository with database session.
        
        Args:
            db: Async database session for operations
        """
        super().__init__(Level, db)
    
    async def create(self, subject_id: int, name: str) -> Level:
        """Create a new level record.
        
        Args:
            subject_id: ID of the parent subject
            name: Level name
            
        Returns:
            Created Level instance with all fields populated
            
        Raises:
            IntegrityError: If level with same name already exists for subject
        """
        return await super().create(subject_id=subject_id, name=name)
    
    async def get_by_id(self, id: int) -> Optional[Level]:
        """Retrieve level by ID.
        
        Args:
            id: Level's primary key ID
            
        Returns:
            Level instance if found, None otherwise
        """
        return await super().get_by_id(id)
    
    async def get_by_name(self, subject_id: int, name: str) -> Optional[Level]:
        """Retrieve level by name within a subject.
        
        Args:
            subject_id: ID of the parent subject
            name: Level name to search for
            
        Returns:
            Level instance if found, None otherwise
        """
        result = await self.db.execute(
            select(Level).where(
                (Level.subject_id == subject_id) & (Level.name == name)
            )
        )
        return result.scalar_one_or_none()
    
    async def list_by_subject(
        self, 
        subject_id: int, 
        skip: int = 0, 
        limit: int = 50,
        search: str = None
    ) -> Tuple[List[Level], int]:
        """Fetch paginated levels for a subject with optional search.
        
        Retrieves a paginated list of levels for a specific subject,
        ordered by created_at descending.
        
        Args:
            subject_id: ID of the parent subject
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 50)
            search: Optional search term to filter by name (case-insensitive)
            
        Returns:
            Tuple of (levels, total_count) where levels is a list of Level instances
            and total_count is the total number of levels matching the search criteria
        """
        # Build base query
        query = select(Level).where(Level.subject_id == subject_id)
        count_query = select(func.count(Level.id)).where(Level.subject_id == subject_id)
        
        # Add search filter if provided
        if search:
            search_filter = Level.name.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        # Get total count for subject
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar() or 0
        
        # Get paginated results
        result = await self.db.execute(
            query
            .order_by(Level.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        levels = list(result.scalars().all())
        
        return (levels, total_count)
    
    async def update(self, id: int, name: str) -> Level:
        """Update level by ID.
        
        Args:
            id: Level's primary key ID
            name: New level name
            
        Returns:
            Updated Level instance
            
        Raises:
            ValueError: If level with given ID does not exist
        """
        level = await self.get_by_id(id)
        if level is None:
            raise ValueError(f"Level with id {id} not found")
        
        return await super().update(level, name=name)
    
    async def delete(self, id: int) -> None:
        """Delete level by ID.
        
        Args:
            id: Level's primary key ID
            
        Raises:
            ValueError: If level with given ID does not exist
        """
        level = await self.get_by_id(id)
        if level is None:
            raise ValueError(f"Level with id {id} not found")
        
        await super().delete(level)
