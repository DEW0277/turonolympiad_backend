"""
Test management API endpoints.

This module implements the test management endpoints for subjects, levels,
tests, and questions. All endpoints require admin authentication.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin_user
from app.database import get_db
from app.core.exceptions import (
    ResourceNotFoundError,
    ResourceConflictError,
    ValidationError,
)
from app.models.user import User
from app.schemas.test_management import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
    SubjectListResponse,
    LevelCreate,
    LevelUpdate,
    LevelResponse,
    LevelListResponse,
    TestCreate,
    TestUpdate,
    TestResponse,
    TestListResponse,
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionListResponse,
    ErrorResponse,
)
from app.services.subject_service import SubjectService
from app.services.level_service import LevelService
from app.services.test_service import TestService
from app.services.question_service import QuestionService
from app.repositories.subject_repository import SubjectRepository
from app.repositories.level_repository import LevelRepository
from app.repositories.test_repository import TestRepository
from app.repositories.question_repository import QuestionRepository
from app.services.audit_service import AuditService
from app.repositories.question_option_repository import QuestionOptionRepository

# Initialize router
router = APIRouter(prefix="/api/admin", tags=["test-management"])


# ============================================================================
# SUBJECT ENDPOINTS
# ============================================================================

@router.get(
    "/subjects",
    response_model=SubjectListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_subjects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    search: str = Query(None, description="Search term for filtering by name"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List all subjects with pagination and search."""
    try:
        repo = SubjectRepository(db)
        service = SubjectService(repo)
        subjects, total = await service.list_subjects(skip=skip, limit=limit, search=search)
        return SubjectListResponse(
            items=subjects,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/subjects",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_subject(
    request: SubjectCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new subject."""
    try:
        repo = SubjectRepository(db)
        service = SubjectService(repo)
        subject = await service.create_subject(name=request.name)
        await db.commit()
        await db.refresh(subject)
        return subject
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/subjects/{subject_id}",
    response_model=SubjectResponse,
    status_code=status.HTTP_200_OK,
)
async def get_subject(
    subject_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a subject by ID."""
    try:
        repo = SubjectRepository(db)
        service = SubjectService(repo)
        subject = await service.get_subject(subject_id)
        return subject
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/subjects/{subject_id}",
    response_model=SubjectResponse,
    status_code=status.HTTP_200_OK,
)
async def update_subject(
    subject_id: int,
    request: SubjectUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a subject."""
    try:
        repo = SubjectRepository(db)
        service = SubjectService(repo)
        subject = await service.update_subject(subject_id, name=request.name)
        await db.commit()
        return subject
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/subjects/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_subject(
    subject_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a subject."""
    try:
        repo = SubjectRepository(db)
        service = SubjectService(repo)
        await service.delete_subject(subject_id)
        await db.commit()
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# LEVEL ENDPOINTS
# ============================================================================

@router.get(
    "/subjects/{subject_id}/levels",
    response_model=LevelListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_levels(
    subject_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    search: str = Query(None, description="Search term for filtering by name"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List levels for a subject with search."""
    try:
        level_repo = LevelRepository(db)
        subject_repo = SubjectRepository(db)
        service = LevelService(level_repo, subject_repo)
        levels, total = await service.list_levels(subject_id, skip=skip, limit=limit, search=search)
        return LevelListResponse(
            items=levels,
            total=total,
            skip=skip,
            limit=limit
        )
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/subjects/{subject_id}/levels",
    response_model=LevelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_level(
    subject_id: int,
    request: LevelCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new level."""
    try:
        level_repo = LevelRepository(db)
        subject_repo = SubjectRepository(db)
        service = LevelService(level_repo, subject_repo)
        level = await service.create_level(subject_id, name=request.name)
        await db.commit()
        await db.refresh(level)
        return level
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/subjects/{subject_id}/levels/{level_id}",
    response_model=LevelResponse,
    status_code=status.HTTP_200_OK,
)
async def get_level(
    subject_id: int,
    level_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a level by ID."""
    try:
        level_repo = LevelRepository(db)
        subject_repo = SubjectRepository(db)
        service = LevelService(level_repo, subject_repo)
        level = await service.get_level(level_id)
        return level
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/subjects/{subject_id}/levels/{level_id}",
    response_model=LevelResponse,
    status_code=status.HTTP_200_OK,
)
async def update_level(
    subject_id: int,
    level_id: int,
    request: LevelUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a level."""
    try:
        level_repo = LevelRepository(db)
        subject_repo = SubjectRepository(db)
        service = LevelService(level_repo, subject_repo)
        level = await service.update_level(level_id, name=request.name)
        await db.commit()
        return level
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/subjects/{subject_id}/levels/{level_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_level(
    subject_id: int,
    level_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a level."""
    try:
        level_repo = LevelRepository(db)
        subject_repo = SubjectRepository(db)
        service = LevelService(level_repo, subject_repo)
        await service.delete_level(level_id)
        await db.commit()
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TEST ENDPOINTS
# ============================================================================

@router.get(
    "/levels/{level_id}/tests",
    response_model=TestListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_tests(
    level_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    search: str = Query(None, description="Search term for filtering by name"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List tests for a level with search."""
    try:
        test_repo = TestRepository(db)
        level_repo = LevelRepository(db)
        service = TestService(test_repo, level_repo)
        tests, total = await service.list_tests(level_id, skip=skip, limit=limit, search=search)
        return TestListResponse(
            items=tests,
            total=total,
            skip=skip,
            limit=limit
        )
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/levels/{level_id}/tests",
    response_model=TestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_test(
    level_id: int,
    request: TestCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new test."""
    try:
        test_repo = TestRepository(db)
        level_repo = LevelRepository(db)
        service = TestService(test_repo, level_repo)
        test = await service.create_test(
            level_id,
            name=request.name,
            start_date=request.start_date,
            end_date=request.end_date
        )
        await db.commit()
        await db.refresh(test)
        return test
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/levels/{level_id}/tests/{test_id}",
    response_model=TestResponse,
    status_code=status.HTTP_200_OK,
)
async def get_test(
    level_id: int,
    test_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a test by ID."""
    try:
        test_repo = TestRepository(db)
        level_repo = LevelRepository(db)
        service = TestService(test_repo, level_repo)
        test = await service.get_test(test_id)
        return test
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/levels/{level_id}/tests/{test_id}",
    response_model=TestResponse,
    status_code=status.HTTP_200_OK,
)
async def update_test(
    level_id: int,
    test_id: int,
    request: TestUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a test."""
    try:
        test_repo = TestRepository(db)
        level_repo = LevelRepository(db)
        service = TestService(test_repo, level_repo)
        test = await service.update_test(
            test_id,
            name=request.name,
            start_date=request.start_date,
            end_date=request.end_date
        )
        await db.commit()
        return test
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/levels/{level_id}/tests/{test_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_test(
    level_id: int,
    test_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a test."""
    try:
        test_repo = TestRepository(db)
        level_repo = LevelRepository(db)
        service = TestService(test_repo, level_repo)
        await service.delete_test(test_id)
        await db.commit()
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# QUESTION ENDPOINTS
# ============================================================================

@router.get(
    "/tests/{test_id}/questions",
    response_model=QuestionListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_questions(
    test_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum records to return"),
    search: str = Query(None, description="Search term for filtering by question text"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List questions for a test with search."""
    try:
        question_repo = QuestionRepository(db)
        option_repo = QuestionOptionRepository(db)
        test_repo = TestRepository(db)
        service = QuestionService(question_repo, option_repo, test_repo)
        questions, total = await service.list_questions(test_id, skip=skip, limit=limit, search=search)
        return QuestionListResponse(
            items=questions,
            total=total,
            skip=skip,
            limit=limit
        )
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/tests/{test_id}/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_question(
    test_id: int,
    request: QuestionCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new question."""
    try:
        question_repo = QuestionRepository(db)
        option_repo = QuestionOptionRepository(db)
        test_repo = TestRepository(db)
        service = QuestionService(question_repo, option_repo, test_repo)
        question = await service.create_question(
            test_id,
            text=request.text,
            correct_answer=request.correct_answer,
            options=[{"label": opt.label, "text": opt.text} for opt in request.options]
        )
        await db.commit()
        
        # Reload the question with eagerly loaded options to avoid lazy loading issues
        question_with_options = await question_repo.get_by_id(question.id)
        return question_with_options
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/tests/{test_id}/questions/{question_id}",
    response_model=QuestionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_question(
    test_id: int,
    question_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a question by ID."""
    try:
        question_repo = QuestionRepository(db)
        option_repo = QuestionOptionRepository(db)
        test_repo = TestRepository(db)
        service = QuestionService(question_repo, option_repo, test_repo)
        question = await service.get_question(question_id)
        return question
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/tests/{test_id}/questions/{question_id}",
    response_model=QuestionResponse,
    status_code=status.HTTP_200_OK,
)
async def update_question(
    test_id: int,
    question_id: int,
    request: QuestionUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a question."""
    try:
        question_repo = QuestionRepository(db)
        option_repo = QuestionOptionRepository(db)
        test_repo = TestRepository(db)
        service = QuestionService(question_repo, option_repo, test_repo)
        question = await service.update_question(
            question_id,
            text=request.text,
            correct_answer=request.correct_answer,
            options=[{"label": opt.label, "text": opt.text} for opt in request.options]
        )
        await db.commit()
        return question
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/tests/{test_id}/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_question(
    test_id: int,
    question_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a question."""
    try:
        question_repo = QuestionRepository(db)
        option_repo = QuestionOptionRepository(db)
        test_repo = TestRepository(db)
        service = QuestionService(question_repo, option_repo, test_repo)
        await service.delete_question(question_id)
        await db.commit()
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
