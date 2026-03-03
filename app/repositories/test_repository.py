"""Test repository for database operations.

This module provides the TestRepository class for managing test data persistence,
implementing all database operations for the Test model.
"""

from typing import Optional, Tuple, List
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test import Test
from app.repositories.base import BaseRepository


class TestRepository(BaseRepository[Test]):
    """Repository for Test model database operations.
    
    Handles all database operations for test records including creation,
    retrieval, updates, and deletion. Uses async database operations
    for optimal performance.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize TestRepository with database session.
        
        Args:
            db: Async database session for operations
        """
        super().__init__(Test, db)
    
    async def create(
        self, 
        level_id: int, 
        name: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Test:
        """Create a new test record.
        
        Args:
            level_id: ID of the parent level
            name: Test name
            start_date: Optional start date for test availability
            end_date: Optional end date for test availability
            
        Returns:
            Created Test instance with all fields populated
            
        Raises:
            IntegrityError: If test with same name already exists for level
        """
        return await super().create(
            level_id=level_id,
            name=name,
            start_date=start_date,
            end_date=end_date
        )
    
    async def get_by_id(self, id: int) -> Optional[Test]:
        """Retrieve test by ID.
        
        Args:
            id: Test's primary key ID
            
        Returns:
            Test instance if found, None otherwise
        """
        return await super().get_by_id(id)
    
    async def get_by_name(self, level_id: int, name: str) -> Optional[Test]:
        """Retrieve test by name within a level.
        
        Args:
            level_id: ID of the parent level
            name: Test name to search for
            
        Returns:
            Test instance if found, None otherwise
        """
        result = await self.db.execute(
            select(Test).where(
                (Test.level_id == level_id) & (Test.name == name)
            )
        )
        return result.scalar_one_or_none()
    
    async def list_by_level(
        self, 
        level_id: int, 
        skip: int = 0, 
        limit: int = 50
    ) -> Tuple[List[Test], int]:
        """Fetch paginated tests for a level.
        
        Retrieves a paginated list of tests for a specific level,
        ordered by created_at descending.
        
        Args:
            level_id: ID of the parent level
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 50)
            
        Returns:
            Tuple of (tests, total_count) where tests is a list of Test instances
            and total_count is the total number of tests for the level
        """
        # Get total count for level
        count_result = await self.db.execute(
            select(func.count(Test.id)).where(Test.level_id == level_id)
        )
        total_count = count_result.scalar() or 0
        
        # Get paginated results
        result = await self.db.execute(
            select(Test)
            .where(Test.level_id == level_id)
            .order_by(Test.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        tests = list(result.scalars().all())
        
        return (tests, total_count)
    
    async def update(
        self, 
        id: int, 
        name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Test:
        """Update test by ID.
        
        Args:
            id: Test's primary key ID
            name: New test name
            start_date: New start date (or None to keep existing)
            end_date: New end date (or None to keep existing)
            
        Returns:
            Updated Test instance
            
        Raises:
            ValueError: If test with given ID does not exist
        """
        test = await self.get_by_id(id)
        if test is None:
            raise ValueError(f"Test with id {id} not found")
        
        return await super().update(
            test,
            name=name,
            start_date=start_date,
            end_date=end_date
        )
    
    async def delete(self, id: int) -> None:
        """Delete test by ID.
        
        Args:
            id: Test's primary key ID
            
        Raises:
            ValueError: If test with given ID does not exist
        """
        test = await self.get_by_id(id)
        if test is None:
            raise ValueError(f"Test with id {id} not found")
        
        await super().delete(test)
