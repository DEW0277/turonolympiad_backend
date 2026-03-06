"""Subject service for business logic and validation.

This module provides the SubjectService class for managing subject operations,
including creation, retrieval, updates, and deletion with comprehensive validation.
"""

from typing import Tuple, List
from app.models.subject import Subject
from app.repositories.subject_repository import SubjectRepository
from app.core.exceptions import (
    ResourceNotFoundError,
    ResourceConflictError,
    ValidationError
)


class SubjectService:
    """Service for subject business logic and validation.
    
    Handles all subject operations including creation, retrieval, updates,
    and deletion with comprehensive validation and error handling.
    """
    
    def __init__(self, subject_repository: SubjectRepository):
        """Initialize SubjectService with dependencies.
        
        Args:
            subject_repository: SubjectRepository instance for database operations
        """
        self.subject_repo = subject_repository
    
    def _validate_name(self, name: str) -> None:
        """Validate subject name.
        
        Args:
            name: Subject name to validate
            
        Raises:
            ValidationError: If name is invalid
        """
        if not name or not isinstance(name, str):
            raise ValidationError("Subject name must be a non-empty string")
        
        if len(name) < 1 or len(name) > 100:
            raise ValidationError("Subject name must be between 1 and 100 characters")
        
        if name.strip() != name:
            raise ValidationError("Subject name cannot have leading or trailing whitespace")
    
    async def create_subject(self, name: str) -> Subject:
        """Create a new subject.
        
        Args:
            name: Subject name (1-100 characters, must be unique)
            
        Returns:
            Created Subject instance
            
        Raises:
            ValidationError: If name is invalid
            ResourceConflictError: If subject with same name already exists
        """
        self._validate_name(name)
        
        # Check for duplicate
        existing = await self.subject_repo.get_by_name(name)
        if existing:
            raise ResourceConflictError(f"Subject with name '{name}' already exists")
        
        return await self.subject_repo.create(name=name)
    
    async def get_subject(self, subject_id: int) -> Subject:
        """Retrieve a subject by ID.
        
        Args:
            subject_id: Subject ID to retrieve
            
        Returns:
            Subject instance
            
        Raises:
            ResourceNotFoundError: If subject not found
        """
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise ResourceNotFoundError(f"Subject with id {subject_id} not found")
        
        return subject
    
    async def list_subjects(
        self, 
        skip: int = 0, 
        limit: int = 50,
        search: str = None
    ) -> Tuple[List[Subject], int]:
        """List all subjects with pagination and search.
        
        Args:
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 50)
            search: Optional search term to filter by name
            
        Returns:
            Tuple of (subjects, total_count)
        """
        return await self.subject_repo.list(skip=skip, limit=limit, search=search)
    
    async def update_subject(self, subject_id: int, name: str) -> Subject:
        """Update a subject.
        
        Args:
            subject_id: Subject ID to update
            name: New subject name
            
        Returns:
            Updated Subject instance
            
        Raises:
            ValidationError: If name is invalid
            ResourceNotFoundError: If subject not found
            ResourceConflictError: If new name already exists
        """
        self._validate_name(name)
        
        # Verify subject exists
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise ResourceNotFoundError(f"Subject with id {subject_id} not found")
        
        # Check for duplicate if name is different
        if subject.name != name:
            existing = await self.subject_repo.get_by_name(name)
            if existing:
                raise ResourceConflictError(f"Subject with name '{name}' already exists")
        
        return await self.subject_repo.update(subject_id, name=name)
    
    async def delete_subject(self, subject_id: int) -> None:
        """Delete a subject.
        
        Args:
            subject_id: Subject ID to delete
            
        Raises:
            ResourceNotFoundError: If subject not found
        """
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise ResourceNotFoundError(f"Subject with id {subject_id} not found")
        
        await self.subject_repo.delete(subject_id)
