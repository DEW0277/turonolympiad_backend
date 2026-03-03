"""Level service for business logic and validation.

This module provides the LevelService class for managing level operations,
including creation, retrieval, updates, and deletion with comprehensive validation.
"""

from typing import Tuple, List
from app.models.level import Level
from app.repositories.level_repository import LevelRepository
from app.repositories.subject_repository import SubjectRepository
from app.core.exceptions import (
    ResourceNotFoundError,
    ResourceConflictError,
    ValidationError
)


class LevelService:
    """Service for level business logic and validation.
    
    Handles all level operations including creation, retrieval, updates,
    and deletion with comprehensive validation and error handling.
    """
    
    def __init__(
        self, 
        level_repository: LevelRepository,
        subject_repository: SubjectRepository
    ):
        """Initialize LevelService with dependencies.
        
        Args:
            level_repository: LevelRepository instance for database operations
            subject_repository: SubjectRepository instance for subject validation
        """
        self.level_repo = level_repository
        self.subject_repo = subject_repository
    
    def _validate_name(self, name: str) -> None:
        """Validate level name.
        
        Args:
            name: Level name to validate
            
        Raises:
            ValidationError: If name is invalid
        """
        if not name or not isinstance(name, str):
            raise ValidationError("Level name must be a non-empty string")
        
        if len(name) < 1 or len(name) > 100:
            raise ValidationError("Level name must be between 1 and 100 characters")
        
        if name.strip() != name:
            raise ValidationError("Level name cannot have leading or trailing whitespace")
    
    async def create_level(self, subject_id: int, name: str) -> Level:
        """Create a new level.
        
        Args:
            subject_id: Parent subject ID
            name: Level name (1-100 characters, must be unique within subject)
            
        Returns:
            Created Level instance
            
        Raises:
            ValidationError: If name is invalid
            ResourceNotFoundError: If subject not found
            ResourceConflictError: If level with same name already exists in subject
        """
        self._validate_name(name)
        
        # Verify subject exists
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise ResourceNotFoundError(f"Subject with id {subject_id} not found")
        
        # Check for duplicate within subject
        existing = await self.level_repo.get_by_name(subject_id, name)
        if existing:
            raise ResourceConflictError(
                f"Level with name '{name}' already exists in subject {subject_id}"
            )
        
        return await self.level_repo.create(subject_id=subject_id, name=name)
    
    async def get_level(self, level_id: int) -> Level:
        """Retrieve a level by ID.
        
        Args:
            level_id: Level ID to retrieve
            
        Returns:
            Level instance
            
        Raises:
            ResourceNotFoundError: If level not found
        """
        level = await self.level_repo.get_by_id(level_id)
        if not level:
            raise ResourceNotFoundError(f"Level with id {level_id} not found")
        
        return level
    
    async def list_levels(
        self, 
        subject_id: int,
        skip: int = 0, 
        limit: int = 50
    ) -> Tuple[List[Level], int]:
        """List levels for a subject with pagination.
        
        Args:
            subject_id: Parent subject ID
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 50)
            
        Returns:
            Tuple of (levels, total_count)
            
        Raises:
            ResourceNotFoundError: If subject not found
        """
        # Verify subject exists
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise ResourceNotFoundError(f"Subject with id {subject_id} not found")
        
        return await self.level_repo.list_by_subject(
            subject_id=subject_id,
            skip=skip,
            limit=limit
        )
    
    async def update_level(self, level_id: int, name: str) -> Level:
        """Update a level.
        
        Args:
            level_id: Level ID to update
            name: New level name
            
        Returns:
            Updated Level instance
            
        Raises:
            ValidationError: If name is invalid
            ResourceNotFoundError: If level not found
            ResourceConflictError: If new name already exists in subject
        """
        self._validate_name(name)
        
        # Verify level exists
        level = await self.level_repo.get_by_id(level_id)
        if not level:
            raise ResourceNotFoundError(f"Level with id {level_id} not found")
        
        # Check for duplicate if name is different
        if level.name != name:
            existing = await self.level_repo.get_by_name(level.subject_id, name)
            if existing:
                raise ResourceConflictError(
                    f"Level with name '{name}' already exists in subject {level.subject_id}"
                )
        
        return await self.level_repo.update(level_id, name=name)
    
    async def delete_level(self, level_id: int) -> None:
        """Delete a level.
        
        Args:
            level_id: Level ID to delete
            
        Raises:
            ResourceNotFoundError: If level not found
        """
        level = await self.level_repo.get_by_id(level_id)
        if not level:
            raise ResourceNotFoundError(f"Level with id {level_id} not found")
        
        await self.level_repo.delete(level_id)
