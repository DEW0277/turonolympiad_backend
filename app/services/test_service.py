"""Test service for business logic and validation.

This module provides the TestService class for managing test operations,
including creation, retrieval, updates, and deletion with comprehensive validation.
"""

from typing import Tuple, List, Optional
from datetime import datetime
from app.models.test import Test
from app.repositories.test_repository import TestRepository
from app.repositories.level_repository import LevelRepository
from app.core.exceptions import (
    ResourceNotFoundError,
    ResourceConflictError,
    ValidationError
)


class TestService:
    """Service for test business logic and validation.
    
    Handles all test operations including creation, retrieval, updates,
    and deletion with comprehensive validation and error handling.
    """
    
    def __init__(
        self, 
        test_repository: TestRepository,
        level_repository: LevelRepository
    ):
        """Initialize TestService with dependencies.
        
        Args:
            test_repository: TestRepository instance for database operations
            level_repository: LevelRepository instance for level validation
        """
        self.test_repo = test_repository
        self.level_repo = level_repository
    
    def _validate_name(self, name: str) -> None:
        """Validate test name.
        
        Args:
            name: Test name to validate
            
        Raises:
            ValidationError: If name is invalid
        """
        if not name or not isinstance(name, str):
            raise ValidationError("Test name must be a non-empty string")
        
        if len(name) < 1 or len(name) > 100:
            raise ValidationError("Test name must be between 1 and 100 characters")
        
        if name.strip() != name:
            raise ValidationError("Test name cannot have leading or trailing whitespace")
    
    def _validate_dates(
        self, 
        start_date: Optional[datetime], 
        end_date: Optional[datetime]
    ) -> None:
        """Validate test dates.
        
        Args:
            start_date: Test start date
            end_date: Test end date
            
        Raises:
            ValidationError: If dates are invalid
        """
        if start_date is not None and not isinstance(start_date, datetime):
            raise ValidationError("start_date must be a datetime object")
        
        if end_date is not None and not isinstance(end_date, datetime):
            raise ValidationError("end_date must be a datetime object")
        
        if start_date is not None and end_date is not None:
            if end_date < start_date:
                raise ValidationError("end_date must be greater than or equal to start_date")
    
    async def create_test(
        self, 
        level_id: int, 
        name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Test:
        """Create a new test.
        
        Args:
            level_id: Parent level ID
            name: Test name (1-100 characters, must be unique within level)
            start_date: Optional test start date
            end_date: Optional test end date
            
        Returns:
            Created Test instance
            
        Raises:
            ValidationError: If name or dates are invalid
            ResourceNotFoundError: If level not found
            ResourceConflictError: If test with same name already exists in level
        """
        self._validate_name(name)
        self._validate_dates(start_date, end_date)
        
        # Verify level exists
        level = await self.level_repo.get_by_id(level_id)
        if not level:
            raise ResourceNotFoundError(f"Level with id {level_id} not found")
        
        # Check for duplicate within level
        existing = await self.test_repo.get_by_name(level_id, name)
        if existing:
            raise ResourceConflictError(
                f"Test with name '{name}' already exists in level {level_id}"
            )
        
        return await self.test_repo.create(
            level_id=level_id,
            name=name,
            start_date=start_date,
            end_date=end_date
        )
    
    async def get_test(self, test_id: int) -> Test:
        """Retrieve a test by ID.
        
        Args:
            test_id: Test ID to retrieve
            
        Returns:
            Test instance
            
        Raises:
            ResourceNotFoundError: If test not found
        """
        test = await self.test_repo.get_by_id(test_id)
        if not test:
            raise ResourceNotFoundError(f"Test with id {test_id} not found")
        
        return test
    
    async def list_tests(
        self, 
        level_id: int,
        skip: int = 0, 
        limit: int = 50,
        search: str = None
    ) -> Tuple[List[Test], int]:
        """List tests for a level with pagination and search.
        
        Args:
            level_id: Parent level ID
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 50)
            search: Optional search term to filter by name
            
        Returns:
            Tuple of (tests, total_count)
            
        Raises:
            ResourceNotFoundError: If level not found
        """
        # Verify level exists
        level = await self.level_repo.get_by_id(level_id)
        if not level:
            raise ResourceNotFoundError(f"Level with id {level_id} not found")
        
        return await self.test_repo.list_by_level(
            level_id=level_id,
            skip=skip,
            limit=limit,
            search=search
        )
    
    async def update_test(
        self, 
        test_id: int, 
        name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Test:
        """Update a test.
        
        Args:
            test_id: Test ID to update
            name: New test name
            start_date: New start date (or None to keep existing)
            end_date: New end date (or None to keep existing)
            
        Returns:
            Updated Test instance
            
        Raises:
            ValidationError: If name or dates are invalid
            ResourceNotFoundError: If test not found
            ResourceConflictError: If new name already exists in level
        """
        self._validate_name(name)
        self._validate_dates(start_date, end_date)
        
        # Verify test exists
        test = await self.test_repo.get_by_id(test_id)
        if not test:
            raise ResourceNotFoundError(f"Test with id {test_id} not found")
        
        # Check for duplicate if name is different
        if test.name != name:
            existing = await self.test_repo.get_by_name(test.level_id, name)
            if existing:
                raise ResourceConflictError(
                    f"Test with name '{name}' already exists in level {test.level_id}"
                )
        
        return await self.test_repo.update(
            test_id,
            name=name,
            start_date=start_date,
            end_date=end_date
        )
    
    async def delete_test(self, test_id: int) -> None:
        """Delete a test.
        
        Args:
            test_id: Test ID to delete
            
        Raises:
            ResourceNotFoundError: If test not found
        """
        test = await self.test_repo.get_by_id(test_id)
        if not test:
            raise ResourceNotFoundError(f"Test with id {test_id} not found")
        
        await self.test_repo.delete(test_id)
