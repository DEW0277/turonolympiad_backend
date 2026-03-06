"""Question service for business logic and validation.

This module provides the QuestionService class for managing question operations,
including creation, retrieval, updates, and deletion with comprehensive validation.
"""

from typing import Tuple, List, Dict
from app.models.question import Question
from app.repositories.question_repository import QuestionRepository
from app.repositories.question_option_repository import QuestionOptionRepository
from app.repositories.test_repository import TestRepository
from app.core.exceptions import (
    ResourceNotFoundError,
    ResourceConflictError,
    ValidationError
)


class QuestionService:
    """Service for question business logic and validation.
    
    Handles all question operations including creation, retrieval, updates,
    and deletion with comprehensive validation and error handling.
    """
    
    def __init__(
        self, 
        question_repository: QuestionRepository,
        question_option_repository: QuestionOptionRepository,
        test_repository: TestRepository
    ):
        """Initialize QuestionService with dependencies.
        
        Args:
            question_repository: QuestionRepository instance for database operations
            question_option_repository: QuestionOptionRepository for option operations
            test_repository: TestRepository instance for test validation
        """
        self.question_repo = question_repository
        self.option_repo = question_option_repository
        self.test_repo = test_repository
    
    def _validate_text(self, text: str) -> None:
        """Validate question text.
        
        Args:
            text: Question text to validate
            
        Raises:
            ValidationError: If text is invalid
        """
        if not text or not isinstance(text, str):
            raise ValidationError("Question text must be a non-empty string")
        
        if len(text) < 1 or len(text) > 1000:
            raise ValidationError("Question text must be between 1 and 1000 characters")
        
        if text.strip() != text:
            raise ValidationError("Question text cannot have leading or trailing whitespace")
    
    def _validate_options(
        self, 
        options: List[Dict[str, str]], 
        correct_answer: str
    ) -> None:
        """Validate question options.
        
        Args:
            options: List of option dictionaries with 'label' and 'text' keys
            correct_answer: Correct answer label (A-J)
            
        Raises:
            ValidationError: If options are invalid
        """
        if not isinstance(options, list):
            raise ValidationError("Options must be a list")
        
        if len(options) < 3 or len(options) > 10:
            raise ValidationError("Question must have 3 to 10 options")
        
        valid_labels = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'}
        seen_labels = set()
        seen_texts = set()
        
        for i, option in enumerate(options):
            if not isinstance(option, dict):
                raise ValidationError(f"Option {i} must be a dictionary")
            
            if 'label' not in option or 'text' not in option:
                raise ValidationError(f"Option {i} must have 'label' and 'text' keys")
            
            label = option['label']
            text = option['text']
            
            if not isinstance(label, str) or label not in valid_labels:
                raise ValidationError(f"Option {i} label must be A-J")
            
            if not isinstance(text, str) or not text:
                raise ValidationError(f"Option {i} text must be a non-empty string")
            
            if len(text) > 500:
                raise ValidationError(f"Option {i} text must not exceed 500 characters")
            
            if label in seen_labels:
                raise ValidationError(f"Duplicate option label: {label}")
            
            if text in seen_texts:
                raise ValidationError("Duplicate option text")
            
            seen_labels.add(label)
            seen_texts.add(text)
        
        # Verify correct_answer matches one of the option labels
        if correct_answer not in seen_labels:
            raise ValidationError(
                f"correct_answer '{correct_answer}' must match one of the option labels"
            )
    
    async def create_question(
        self, 
        test_id: int, 
        text: str, 
        correct_answer: str,
        options: List[Dict[str, str]]
    ) -> Question:
        """Create a new question.
        
        Args:
            test_id: Parent test ID
            text: Question text (1-1000 characters)
            correct_answer: Correct answer label (A-J)
            options: List of 3-10 option dictionaries with 'label' and 'text' keys
            
        Returns:
            Created Question instance with options
            
        Raises:
            ValidationError: If text, correct_answer, or options are invalid
            ResourceNotFoundError: If test not found
        """
        self._validate_text(text)
        self._validate_options(options, correct_answer)
        
        # Verify test exists
        test = await self.test_repo.get_by_id(test_id)
        if not test:
            raise ResourceNotFoundError(f"Test with id {test_id} not found")
        
        # Create question
        question = await self.question_repo.create(
            test_id=test_id,
            text=text,
            correct_answer=correct_answer
        )
        
        # Create options
        for option in options:
            await self.option_repo.create(
                question_id=question.id,
                label=option['label'],
                text=option['text']
            )
        
        # Reload question with options
        question = await self.question_repo.get_by_id(question.id)
        return question
    
    async def get_question(self, question_id: int) -> Question:
        """Retrieve a question by ID.
        
        Args:
            question_id: Question ID to retrieve
            
        Returns:
            Question instance with options
            
        Raises:
            ResourceNotFoundError: If question not found
        """
        question = await self.question_repo.get_by_id(question_id)
        if not question:
            raise ResourceNotFoundError(f"Question with id {question_id} not found")
        
        return question
    
    async def list_questions(
        self, 
        test_id: int,
        skip: int = 0, 
        limit: int = 100,
        search: str = None
    ) -> Tuple[List[Question], int]:
        """List questions for a test with pagination and search.
        
        Args:
            test_id: Parent test ID
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)
            search: Optional search term to filter by question text
            
        Returns:
            Tuple of (questions, total_count)
            
        Raises:
            ResourceNotFoundError: If test not found
        """
        # Verify test exists
        test = await self.test_repo.get_by_id(test_id)
        if not test:
            raise ResourceNotFoundError(f"Test with id {test_id} not found")
        
        return await self.question_repo.list_by_test(
            test_id=test_id,
            skip=skip,
            limit=limit,
            search=search
        )
    
    async def update_question(
        self, 
        question_id: int, 
        text: str, 
        correct_answer: str,
        options: List[Dict[str, str]]
    ) -> Question:
        """Update a question.
        
        Args:
            question_id: Question ID to update
            text: New question text
            correct_answer: New correct answer label (A-J)
            options: New list of 3-10 option dictionaries
            
        Returns:
            Updated Question instance with options
            
        Raises:
            ValidationError: If text, correct_answer, or options are invalid
            ResourceNotFoundError: If question not found
        """
        self._validate_text(text)
        self._validate_options(options, correct_answer)
        
        # Verify question exists
        question = await self.question_repo.get_by_id(question_id)
        if not question:
            raise ResourceNotFoundError(f"Question with id {question_id} not found")
        
        # Update question
        updated_question = await self.question_repo.update(
            question_id,
            text=text,
            correct_answer=correct_answer
        )
        
        # Delete existing options
        existing_options = await self.option_repo.list_by_question(question_id)
        for option in existing_options:
            await self.option_repo.delete(option.id)
        
        # Create new options
        for option in options:
            await self.option_repo.create(
                question_id=question_id,
                label=option['label'],
                text=option['text']
            )
        
        # Reload question with new options
        updated_question = await self.question_repo.get_by_id(question_id)
        return updated_question
    
    async def delete_question(self, question_id: int) -> None:
        """Delete a question.
        
        Args:
            question_id: Question ID to delete
            
        Raises:
            ResourceNotFoundError: If question not found
        """
        question = await self.question_repo.get_by_id(question_id)
        if not question:
            raise ResourceNotFoundError(f"Question with id {question_id} not found")
        
        await self.question_repo.delete(question_id)
