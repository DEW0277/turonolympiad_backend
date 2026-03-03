"""
Tests for test management system (subjects, levels, tests, questions).

This module contains unit and integration tests for the test management
API endpoints and services.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.subject import Subject
from app.models.level import Level
from app.models.test import Test
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.repositories.subject_repository import SubjectRepository
from app.repositories.level_repository import LevelRepository
from app.repositories.test_repository import TestRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.question_option_repository import QuestionOptionRepository
from app.services.subject_service import SubjectService
from app.services.level_service import LevelService
from app.services.test_service import TestService
from app.services.question_service import QuestionService
from app.core.exceptions import (
    ResourceNotFoundError,
    ResourceConflictError,
    ValidationError,
)


@pytest.fixture
async def db():
    """Create an in-memory SQLite database for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()


# ============================================================================
# SUBJECT SERVICE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_subject(db: AsyncSession):
    """Test creating a subject."""
    repo = SubjectRepository(db)
    service = SubjectService(repo)
    
    subject = await service.create_subject("Mathematics")
    
    assert subject.id is not None
    assert subject.name == "Mathematics"
    assert subject.created_at is not None


@pytest.mark.asyncio
async def test_create_subject_duplicate_name(db: AsyncSession):
    """Test that duplicate subject names are rejected."""
    repo = SubjectRepository(db)
    service = SubjectService(repo)
    
    await service.create_subject("Mathematics")
    
    with pytest.raises(ResourceConflictError):
        await service.create_subject("Mathematics")


@pytest.mark.asyncio
async def test_create_subject_invalid_name_empty(db: AsyncSession):
    """Test that empty subject names are rejected."""
    repo = SubjectRepository(db)
    service = SubjectService(repo)
    
    with pytest.raises(ValidationError):
        await service.create_subject("")


@pytest.mark.asyncio
async def test_create_subject_invalid_name_too_long(db: AsyncSession):
    """Test that subject names > 100 chars are rejected."""
    repo = SubjectRepository(db)
    service = SubjectService(repo)
    
    long_name = "a" * 101
    with pytest.raises(ValidationError):
        await service.create_subject(long_name)


@pytest.mark.asyncio
async def test_get_subject(db: AsyncSession):
    """Test retrieving a subject by ID."""
    repo = SubjectRepository(db)
    service = SubjectService(repo)
    
    created = await service.create_subject("Mathematics")
    retrieved = await service.get_subject(created.id)
    
    assert retrieved.id == created.id
    assert retrieved.name == "Mathematics"


@pytest.mark.asyncio
async def test_get_subject_not_found(db: AsyncSession):
    """Test that retrieving non-existent subject raises error."""
    repo = SubjectRepository(db)
    service = SubjectService(repo)
    
    with pytest.raises(ResourceNotFoundError):
        await service.get_subject(999)


@pytest.mark.asyncio
async def test_list_subjects(db: AsyncSession):
    """Test listing subjects with pagination."""
    repo = SubjectRepository(db)
    service = SubjectService(repo)
    
    await service.create_subject("Mathematics")
    await service.create_subject("Physics")
    await service.create_subject("Chemistry")
    
    subjects, total = await service.list_subjects(skip=0, limit=10)
    
    assert len(subjects) == 3
    assert total == 3


@pytest.mark.asyncio
async def test_update_subject(db: AsyncSession):
    """Test updating a subject."""
    repo = SubjectRepository(db)
    service = SubjectService(repo)
    
    created = await service.create_subject("Mathematics")
    updated = await service.update_subject(created.id, "Advanced Mathematics")
    
    assert updated.name == "Advanced Mathematics"


@pytest.mark.asyncio
async def test_delete_subject(db: AsyncSession):
    """Test deleting a subject."""
    repo = SubjectRepository(db)
    service = SubjectService(repo)
    
    created = await service.create_subject("Mathematics")
    await service.delete_subject(created.id)
    
    with pytest.raises(ResourceNotFoundError):
        await service.get_subject(created.id)


# ============================================================================
# LEVEL SERVICE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_level(db: AsyncSession):
    """Test creating a level."""
    subject_repo = SubjectRepository(db)
    level_repo = LevelRepository(db)
    subject_service = SubjectService(subject_repo)
    level_service = LevelService(level_repo, subject_repo)
    
    subject = await subject_service.create_subject("Mathematics")
    level = await level_service.create_level(subject.id, "Grade 5")
    
    assert level.id is not None
    assert level.subject_id == subject.id
    assert level.name == "Grade 5"


@pytest.mark.asyncio
async def test_create_level_duplicate_name_in_subject(db: AsyncSession):
    """Test that duplicate level names within subject are rejected."""
    subject_repo = SubjectRepository(db)
    level_repo = LevelRepository(db)
    subject_service = SubjectService(subject_repo)
    level_service = LevelService(level_repo, subject_repo)
    
    subject = await subject_service.create_subject("Mathematics")
    await level_service.create_level(subject.id, "Grade 5")
    
    with pytest.raises(ResourceConflictError):
        await level_service.create_level(subject.id, "Grade 5")


@pytest.mark.asyncio
async def test_create_level_subject_not_found(db: AsyncSession):
    """Test that creating level for non-existent subject raises error."""
    level_repo = LevelRepository(db)
    subject_repo = SubjectRepository(db)
    level_service = LevelService(level_repo, subject_repo)
    
    with pytest.raises(ResourceNotFoundError):
        await level_service.create_level(999, "Grade 5")


# ============================================================================
# TEST SERVICE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_test(db: AsyncSession):
    """Test creating a test."""
    subject_repo = SubjectRepository(db)
    level_repo = LevelRepository(db)
    test_repo = TestRepository(db)
    
    subject_service = SubjectService(subject_repo)
    level_service = LevelService(level_repo, subject_repo)
    test_service = TestService(test_repo, level_repo)
    
    subject = await subject_service.create_subject("Mathematics")
    level = await level_service.create_level(subject.id, "Grade 5")
    
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=7)
    
    test = await test_service.create_test(
        level.id,
        "Midterm Exam",
        start_date=start_date,
        end_date=end_date
    )
    
    assert test.id is not None
    assert test.level_id == level.id
    assert test.name == "Midterm Exam"


@pytest.mark.asyncio
async def test_create_test_invalid_date_range(db: AsyncSession):
    """Test that invalid date ranges are rejected."""
    subject_repo = SubjectRepository(db)
    level_repo = LevelRepository(db)
    test_repo = TestRepository(db)
    
    subject_service = SubjectService(subject_repo)
    level_service = LevelService(level_repo, subject_repo)
    test_service = TestService(test_repo, level_repo)
    
    subject = await subject_service.create_subject("Mathematics")
    level = await level_service.create_level(subject.id, "Grade 5")
    
    start_date = datetime.utcnow()
    end_date = start_date - timedelta(days=7)  # End before start
    
    with pytest.raises(ValidationError):
        await test_service.create_test(
            level.id,
            "Midterm Exam",
            start_date=start_date,
            end_date=end_date
        )


# ============================================================================
# QUESTION SERVICE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_question(db: AsyncSession):
    """Test creating a question."""
    subject_repo = SubjectRepository(db)
    level_repo = LevelRepository(db)
    test_repo = TestRepository(db)
    question_repo = QuestionRepository(db)
    option_repo = QuestionOptionRepository(db)
    
    subject_service = SubjectService(subject_repo)
    level_service = LevelService(level_repo, subject_repo)
    test_service = TestService(test_repo, level_repo)
    question_service = QuestionService(question_repo, option_repo, test_repo)
    
    subject = await subject_service.create_subject("Mathematics")
    level = await level_service.create_level(subject.id, "Grade 5")
    test = await test_service.create_test(level.id, "Midterm Exam")
    
    options = [
        {"label": "A", "text": "4"},
        {"label": "B", "text": "5"},
        {"label": "C", "text": "3"},
        {"label": "D", "text": "6"},
    ]
    
    question = await question_service.create_question(
        test.id,
        "What is 2 + 2?",
        "A",
        options
    )
    
    assert question.id is not None
    assert question.test_id == test.id
    assert question.text == "What is 2 + 2?"
    assert question.correct_answer == "A"
    assert len(question.options) == 4


@pytest.mark.asyncio
async def test_create_question_invalid_option_count(db: AsyncSession):
    """Test that invalid option counts are rejected."""
    subject_repo = SubjectRepository(db)
    level_repo = LevelRepository(db)
    test_repo = TestRepository(db)
    question_repo = QuestionRepository(db)
    option_repo = QuestionOptionRepository(db)
    
    subject_service = SubjectService(subject_repo)
    level_service = LevelService(level_repo, subject_repo)
    test_service = TestService(test_repo, level_repo)
    question_service = QuestionService(question_repo, option_repo, test_repo)
    
    subject = await subject_service.create_subject("Mathematics")
    level = await level_service.create_level(subject.id, "Grade 5")
    test = await test_service.create_test(level.id, "Midterm Exam")
    
    options = [
        {"label": "A", "text": "4"},
        {"label": "B", "text": "5"},
    ]  # Only 2 options, need 3-4
    
    with pytest.raises(ValidationError):
        await question_service.create_question(
            test.id,
            "What is 2 + 2?",
            "A",
            options
        )


@pytest.mark.asyncio
async def test_create_question_invalid_correct_answer(db: AsyncSession):
    """Test that invalid correct answers are rejected."""
    subject_repo = SubjectRepository(db)
    level_repo = LevelRepository(db)
    test_repo = TestRepository(db)
    question_repo = QuestionRepository(db)
    option_repo = QuestionOptionRepository(db)
    
    subject_service = SubjectService(subject_repo)
    level_service = LevelService(level_repo, subject_repo)
    test_service = TestService(test_repo, level_repo)
    question_service = QuestionService(question_repo, option_repo, test_repo)
    
    subject = await subject_service.create_subject("Mathematics")
    level = await level_service.create_level(subject.id, "Grade 5")
    test = await test_service.create_test(level.id, "Midterm Exam")
    
    options = [
        {"label": "A", "text": "4"},
        {"label": "B", "text": "5"},
        {"label": "C", "text": "3"},
        {"label": "D", "text": "6"},
    ]
    
    with pytest.raises(ValidationError):
        await question_service.create_question(
            test.id,
            "What is 2 + 2?",
            "E",  # Invalid label
            options
        )
