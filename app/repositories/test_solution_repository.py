"""Test solution repository for database operations.

This module provides the TestSolutionRepository class for managing test solution data persistence,
implementing all database operations for the TestSolution model with optimized queries.
"""

from typing import Optional, List
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_solution import TestSolution
from app.repositories.base import BaseRepository


class TestSolutionRepository(BaseRepository[TestSolution]):
    """Repository for TestSolution model database operations.
    
    Handles all database operations for test solution records including creation,
    retrieval, and querying. Uses async database operations and optimized
    queries with proper indexing for high concurrency support.
    
    Requirements:
        - 4.1: Test solution recording and management
        - 4.3: Solution retrieval and confirmation
        - 4.4: Multiple submission support
        - 4.5: Solution attempt tracking
        - 5.3: Profile API solution retrieval
        - 7.2: Query optimization with indexes
    """
    
    __test__ = False  # Tell pytest this is not a test class
    
    def __init__(self, db: AsyncSession):
        """Initialize TestSolutionRepository with database session.
        
        Args:
            db: Async database session for operations
        """
        super().__init__(TestSolution, db)
    
    async def create(
        self,
        user_id: int,
        test_id: int,
        solution_data: str,
        score: Optional[Decimal] = None
    ) -> TestSolution:
        """Record a new test solution submission.
        
        Creates a test solution record with all required fields. Users can submit
        multiple solutions for the same test, with each submission stored separately.
        
        Args:
            user_id: ID of the user submitting the solution
            test_id: ID of the test being solved
            solution_data: JSON string containing the user's answers
            score: Optional test score (0-100 or None)
            
        Returns:
            Created TestSolution instance with all fields populated
            
        Raises:
            IntegrityError: If user_id or test_id is invalid (foreign key constraint)
            IntegrityError: If score is outside valid range (check constraint)
        """
        return await super().create(
            user_id=user_id,
            test_id=test_id,
            solution_data=solution_data,
            score=score
        )
    
    async def get_by_id(self, solution_id: int) -> Optional[TestSolution]:
        """Retrieve solution by ID with relationships.
        
        Fetches a solution with eager-loaded user and test relationships
        to minimize database queries.
        
        Args:
            solution_id: Solution's primary key ID
            
        Returns:
            TestSolution instance if found, None otherwise
        """
        result = await self.db.execute(
            select(TestSolution)
            .options(
                selectinload(TestSolution.user),
                selectinload(TestSolution.test)
            )
            .where(TestSolution.id == solution_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_solutions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestSolution]:
        """Retrieve all solutions for a user with pagination.
        
        Uses the idx_solution_user_submitted composite index for efficient
        retrieval of user's solution history ordered by submission date.
        
        Args:
            user_id: ID of the user
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            List of TestSolution instances for the user, ordered by submitted_at descending
        """
        result = await self.db.execute(
            select(TestSolution)
            .where(TestSolution.user_id == user_id)
            .options(
                selectinload(TestSolution.test)
            )
            .order_by(TestSolution.submitted_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_user_solutions_for_test(
        self,
        user_id: int,
        test_id: int
    ) -> List[TestSolution]:
        """Retrieve all solutions for a specific user and test.
        
        Uses the idx_solution_user_test composite index for fast lookup.
        Returns all submission attempts for a user on a specific test.
        
        Args:
            user_id: ID of the user
            test_id: ID of the test
            
        Returns:
            List of TestSolution instances for the user-test combination,
            ordered by submitted_at descending
        """
        result = await self.db.execute(
            select(TestSolution)
            .where(
                (TestSolution.user_id == user_id) & (TestSolution.test_id == test_id)
            )
            .order_by(TestSolution.submitted_at.desc())
        )
        return list(result.scalars().all())
