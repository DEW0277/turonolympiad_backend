"""Tests for TestSolutionRepository.

This module contains comprehensive tests for the TestSolutionRepository class,
validating all database operations for test solution management.
"""

import pytest
import pytest_asyncio
import json
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.user import User
from app.models.test import Test
from app.models.test_solution import TestSolution
from app.models.level import Level
from app.models.subject import Subject
from app.repositories.test_solution_repository import TestSolutionRepository
from app.services.password_service import PasswordService


@pytest_asyncio.fixture
async def solution_repo(test_db):
    """Create a TestSolutionRepository instance."""
    async with test_db() as session:
        yield TestSolutionRepository(session)


@pytest_asyncio.fixture
async def test_user(test_db):
    """Create a test user."""
    async with test_db() as session:
        password_service = PasswordService()
        user = User(
            email="testuser@example.com",
            hashed_password=password_service.hash_password("password123"),
            is_verified=True,
            is_admin=False
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def test_subject(test_db):
    """Create a test subject."""
    async with test_db() as session:
        subject = Subject(name="Mathematics")
        session.add(subject)
        await session.commit()
        await session.refresh(subject)
        return subject


@pytest_asyncio.fixture
async def test_level(test_db, test_subject):
    """Create a test level."""
    async with test_db() as session:
        level = Level(
            subject_id=test_subject.id,
            name="Level 1"
        )
        session.add(level)
        await session.commit()
        await session.refresh(level)
        return level


@pytest_asyncio.fixture
async def test_test(test_db, test_level):
    """Create a test."""
    async with test_db() as session:
        test = Test(
            level_id=test_level.id,
            name_en="Test 1",
            name_ru="Тест 1",
            name_uz="Test 1",
            price=Decimal("50.00"),
            start_date=None,
            end_date=None
        )
        session.add(test)
        await session.commit()
        await session.refresh(test)
        return test


class TestSolutionRepositoryCreate:
    """Tests for TestSolutionRepository.create() method."""
    
    async def test_create_solution_with_valid_data(self, test_db, test_user, test_test):
        """Test creating a solution with valid data."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            solution_data = json.dumps({"answers": [1, 2, 3]})
            solution = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=solution_data,
                score=Decimal("85.50")
            )
            
            assert solution.id is not None
            assert solution.user_id == test_user.id
            assert solution.test_id == test_test.id
            assert solution.solution_data == solution_data
            assert solution.score == Decimal("85.50")
            assert solution.submitted_at is not None
            assert solution.created_at is not None
    
    async def test_create_solution_without_score(self, test_db, test_user, test_test):
        """Test creating a solution without a score."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            solution_data = json.dumps({"answers": [1, 2, 3]})
            solution = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=solution_data,
                score=None
            )
            
            assert solution.score is None
    
    async def test_create_solution_with_zero_score(self, test_db, test_user, test_test):
        """Test creating a solution with zero score."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            solution_data = json.dumps({"answers": []})
            solution = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=solution_data,
                score=Decimal("0.00")
            )
            
            assert solution.score == Decimal("0.00")
    
    async def test_create_solution_with_perfect_score(self, test_db, test_user, test_test):
        """Test creating a solution with perfect score."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            solution_data = json.dumps({"answers": [1, 2, 3, 4, 5]})
            solution = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=solution_data,
                score=Decimal("100.00")
            )
            
            assert solution.score == Decimal("100.00")
    
    async def test_create_solution_with_complex_data(self, test_db, test_user, test_test):
        """Test creating a solution with complex JSON data."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            complex_data = {
                "answers": [
                    {"question_id": 1, "selected_option_id": 3},
                    {"question_id": 2, "selected_option_id": 7},
                    {"question_id": 3, "text_answer": "Some answer"}
                ],
                "metadata": {
                    "time_spent": 1200,
                    "attempts": 2
                }
            }
            solution_data = json.dumps(complex_data)
            
            solution = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=solution_data,
                score=Decimal("75.00")
            )
            
            assert solution.solution_data == solution_data
            # Verify we can parse it back
            parsed = json.loads(solution.solution_data)
            assert parsed["answers"][0]["question_id"] == 1
    
    async def test_create_solution_timestamps_are_set(self, test_db, test_user, test_test):
        """Test that timestamps are automatically set on creation."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            before_create = datetime.now(timezone.utc)
            
            solution = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1, 2, 3]}),
                score=Decimal("80.00")
            )
            
            after_create = datetime.now(timezone.utc)
            
            assert before_create <= solution.submitted_at <= after_create
            assert before_create <= solution.created_at <= after_create


class TestSolutionRepositoryGetById:
    """Tests for TestSolutionRepository.get_by_id() method."""
    
    async def test_get_solution_by_id_success(self, test_db, test_user, test_test):
        """Test retrieving a solution by ID."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            created_solution = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1, 2, 3]}),
                score=Decimal("85.50")
            )
            
            retrieved_solution = await repo.get_by_id(created_solution.id)
            
            assert retrieved_solution is not None
            assert retrieved_solution.id == created_solution.id
            assert retrieved_solution.user_id == test_user.id
            assert retrieved_solution.test_id == test_test.id
            assert retrieved_solution.score == Decimal("85.50")
    
    async def test_get_solution_by_id_not_found(self, test_db):
        """Test retrieving a non-existent solution."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            solution = await repo.get_by_id(99999)
            
            assert solution is None
    
    async def test_get_solution_by_id_loads_relationships(self, test_db, test_user, test_test):
        """Test that get_by_id loads user and test relationships."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            created_solution = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1, 2, 3]}),
                score=Decimal("85.50")
            )
            
            retrieved_solution = await repo.get_by_id(created_solution.id)
            
            # Verify relationships are loaded
            assert retrieved_solution.user is not None
            assert retrieved_solution.user.id == test_user.id
            assert retrieved_solution.test is not None
            assert retrieved_solution.test.id == test_test.id


class TestSolutionRepositoryGetUserSolutions:
    """Tests for TestSolutionRepository.get_user_solutions() method."""
    
    async def test_get_user_solutions_empty(self, test_db, test_user):
        """Test retrieving solutions for user with no solutions."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            solutions = await repo.get_user_solutions(test_user.id)
            
            assert solutions == []
    
    async def test_get_user_solutions_single(self, test_db, test_user, test_test):
        """Test retrieving a single solution for user."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            created_solution = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1, 2, 3]}),
                score=Decimal("85.50")
            )
            
            solutions = await repo.get_user_solutions(test_user.id)
            
            assert len(solutions) == 1
            assert solutions[0].id == created_solution.id
    
    async def test_get_user_solutions_multiple(self, test_db, test_user, test_test, test_level):
        """Test retrieving multiple solutions for user."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            # Create first solution
            solution1 = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1, 2, 3]}),
                score=Decimal("85.50")
            )
            
            # Create second test
            test2 = Test(
                level_id=test_level.id,
                name_en="Test 2",
                name_ru="Тест 2",
                name_uz="Test 2",
                price=Decimal("60.00"),
                start_date=None,
                end_date=None
            )
            session.add(test2)
            await session.commit()
            await session.refresh(test2)
            
            # Create second solution
            solution2 = await repo.create(
                user_id=test_user.id,
                test_id=test2.id,
                solution_data=json.dumps({"answers": [4, 5, 6]}),
                score=Decimal("90.00")
            )
            
            solutions = await repo.get_user_solutions(test_user.id)
            
            assert len(solutions) == 2
            solution_ids = {s.id for s in solutions}
            assert solution1.id in solution_ids
            assert solution2.id in solution_ids
    
    async def test_get_user_solutions_pagination_skip(self, test_db, test_user, test_test):
        """Test pagination with skip parameter."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            # Create 3 solutions
            for i in range(3):
                await repo.create(
                    user_id=test_user.id,
                    test_id=test_test.id,
                    solution_data=json.dumps({"answers": [i]}),
                    score=Decimal("80.00")
                )
            
            # Get with skip=1
            solutions = await repo.get_user_solutions(test_user.id, skip=1, limit=100)
            
            assert len(solutions) == 2
    
    async def test_get_user_solutions_pagination_limit(self, test_db, test_user, test_test):
        """Test pagination with limit parameter."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            # Create 5 solutions
            for i in range(5):
                await repo.create(
                    user_id=test_user.id,
                    test_id=test_test.id,
                    solution_data=json.dumps({"answers": [i]}),
                    score=Decimal("80.00")
                )
            
            # Get with limit=2
            solutions = await repo.get_user_solutions(test_user.id, skip=0, limit=2)
            
            assert len(solutions) == 2
    
    async def test_get_user_solutions_ordered_by_submitted_at(self, test_db, test_user, test_test):
        """Test that solutions are ordered by submitted_at descending."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            # Create solutions
            solution1 = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1]}),
                score=Decimal("80.00")
            )
            
            solution2 = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [2]}),
                score=Decimal("85.00")
            )
            
            solutions = await repo.get_user_solutions(test_user.id)
            
            # Most recent should be first
            assert solutions[0].id == solution2.id
            assert solutions[1].id == solution1.id
    
    async def test_get_user_solutions_loads_test_relationship(self, test_db, test_user, test_test):
        """Test that get_user_solutions loads test relationship."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1, 2, 3]}),
                score=Decimal("85.50")
            )
            
            solutions = await repo.get_user_solutions(test_user.id)
            
            assert len(solutions) == 1
            assert solutions[0].test is not None
            assert solutions[0].test.id == test_test.id


class TestSolutionRepositoryGetUserSolutionsForTest:
    """Tests for TestSolutionRepository.get_user_solutions_for_test() method."""
    
    async def test_get_user_solutions_for_test_empty(self, test_db, test_user, test_test):
        """Test retrieving solutions for user-test combination with no solutions."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            solutions = await repo.get_user_solutions_for_test(test_user.id, test_test.id)
            
            assert solutions == []
    
    async def test_get_user_solutions_for_test_single(self, test_db, test_user, test_test):
        """Test retrieving a single solution for user-test combination."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            created_solution = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1, 2, 3]}),
                score=Decimal("85.50")
            )
            
            solutions = await repo.get_user_solutions_for_test(test_user.id, test_test.id)
            
            assert len(solutions) == 1
            assert solutions[0].id == created_solution.id
    
    async def test_get_user_solutions_for_test_multiple_submissions(self, test_db, test_user, test_test):
        """Test retrieving multiple submissions for same user-test combination."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            # Create first submission
            solution1 = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1, 2, 3]}),
                score=Decimal("80.00")
            )
            
            # Create second submission
            solution2 = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1, 2, 4]}),
                score=Decimal("85.00")
            )
            
            solutions = await repo.get_user_solutions_for_test(test_user.id, test_test.id)
            
            assert len(solutions) == 2
            solution_ids = {s.id for s in solutions}
            assert solution1.id in solution_ids
            assert solution2.id in solution_ids
    
    async def test_get_user_solutions_for_test_different_user(self, test_db, test_user, test_test):
        """Test that solutions for different user are not returned."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            # Create solution for test_user
            await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1, 2, 3]}),
                score=Decimal("85.50")
            )
            
            # Create another user
            password_service = PasswordService()
            other_user = User(
                email="otheruser@example.com",
                hashed_password=password_service.hash_password("password123"),
                is_verified=True,
                is_admin=False
            )
            session.add(other_user)
            await session.commit()
            await session.refresh(other_user)
            
            # Try to get solutions for other user
            solutions = await repo.get_user_solutions_for_test(other_user.id, test_test.id)
            
            assert solutions == []
    
    async def test_get_user_solutions_for_test_different_test(self, test_db, test_user, test_test, test_level):
        """Test that solutions for different test are not returned."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            # Create solution for test_test
            await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1, 2, 3]}),
                score=Decimal("85.50")
            )
            
            # Create another test
            other_test = Test(
                level_id=test_level.id,
                name_en="Test 2",
                name_ru="Тест 2",
                name_uz="Test 2",
                price=Decimal("60.00"),
                start_date=None,
                end_date=None
            )
            session.add(other_test)
            await session.commit()
            await session.refresh(other_test)
            
            # Try to get solutions for other test
            solutions = await repo.get_user_solutions_for_test(test_user.id, other_test.id)
            
            assert solutions == []
    
    async def test_get_user_solutions_for_test_ordered_by_submitted_at(self, test_db, test_user, test_test):
        """Test that solutions are ordered by submitted_at descending."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            # Create solutions
            solution1 = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1]}),
                score=Decimal("80.00")
            )
            
            solution2 = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [2]}),
                score=Decimal("85.00")
            )
            
            solutions = await repo.get_user_solutions_for_test(test_user.id, test_test.id)
            
            # Most recent should be first
            assert solutions[0].id == solution2.id
            assert solutions[1].id == solution1.id


class TestSolutionRepositoryIntegration:
    """Integration tests for TestSolutionRepository."""
    
    async def test_complete_solution_workflow(self, test_db, test_user, test_test):
        """Test complete solution workflow: create, retrieve, query."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            # Create solution
            solution = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1, 2, 3]}),
                score=Decimal("85.50")
            )
            
            # Retrieve by ID
            retrieved = await repo.get_by_id(solution.id)
            assert retrieved is not None
            assert retrieved.id == solution.id
            
            # Get all user solutions
            all_solutions = await repo.get_user_solutions(test_user.id)
            assert len(all_solutions) == 1
            assert all_solutions[0].id == solution.id
            
            # Get solutions for specific test
            test_solutions = await repo.get_user_solutions_for_test(test_user.id, test_test.id)
            assert len(test_solutions) == 1
            assert test_solutions[0].id == solution.id
    
    async def test_multiple_submissions_same_test(self, test_db, test_user, test_test):
        """Test multiple submissions for the same test."""
        async with test_db() as session:
            repo = TestSolutionRepository(session)
            
            # First submission
            solution1 = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1, 2, 3]}),
                score=Decimal("70.00")
            )
            
            # Second submission (improved)
            solution2 = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1, 2, 4]}),
                score=Decimal("85.00")
            )
            
            # Third submission (best)
            solution3 = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                solution_data=json.dumps({"answers": [1, 2, 4, 5]}),
                score=Decimal("95.00")
            )
            
            # Verify all are stored
            all_solutions = await repo.get_user_solutions_for_test(test_user.id, test_test.id)
            assert len(all_solutions) == 3
            
            # Verify ordering (most recent first)
            assert all_solutions[0].id == solution3.id
            assert all_solutions[1].id == solution2.id
            assert all_solutions[2].id == solution1.id
            
            # Verify scores are different
            assert all_solutions[0].score == Decimal("95.00")
            assert all_solutions[1].score == Decimal("85.00")
            assert all_solutions[2].score == Decimal("70.00")
