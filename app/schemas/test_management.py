"""Test management request and response schemas.

This module defines Pydantic models for test management API requests and responses,
including subjects, levels, tests, and questions with comprehensive validation.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime


# ============================================================================
# SUBJECT SCHEMAS
# ============================================================================

class SubjectCreate(BaseModel):
    """Request schema for creating a subject."""
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Subject name (1-100 characters)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Mathematics"
            }
        }
    )


class SubjectUpdate(BaseModel):
    """Request schema for updating a subject."""
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Subject name (1-100 characters)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Advanced Mathematics"
            }
        }
    )


class SubjectResponse(BaseModel):
    """Response schema for subject data."""
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Mathematics",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
    )


# ============================================================================
# LEVEL SCHEMAS
# ============================================================================

class LevelCreate(BaseModel):
    """Request schema for creating a level."""
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Level name (1-100 characters)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Grade 5"
            }
        }
    )


class LevelUpdate(BaseModel):
    """Request schema for updating a level."""
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Level name (1-100 characters)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Grade 6"
            }
        }
    )


class LevelResponse(BaseModel):
    """Response schema for level data."""
    id: int
    subject_id: int
    name: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "subject_id": 1,
                "name": "Grade 5",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
    )


# ============================================================================
# TEST SCHEMAS
# ============================================================================

class TestCreate(BaseModel):
    """Request schema for creating a test."""
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Test name (1-100 characters)"
    )
    start_date: Optional[datetime] = Field(
        default=None,
        description="Test start date (optional)"
    )
    end_date: Optional[datetime] = Field(
        default=None,
        description="Test end date (optional)"
    )
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Validate that end_date >= start_date."""
        if v is not None and info.data.get('start_date') is not None:
            if v < info.data['start_date']:
                raise ValueError('end_date must be greater than or equal to start_date')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Midterm Exam",
                "start_date": "2024-02-01T00:00:00",
                "end_date": "2024-02-15T23:59:59"
            }
        }
    )


class TestUpdate(BaseModel):
    """Request schema for updating a test."""
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Test name (1-100 characters)"
    )
    start_date: Optional[datetime] = Field(
        default=None,
        description="Test start date (optional)"
    )
    end_date: Optional[datetime] = Field(
        default=None,
        description="Test end date (optional)"
    )
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Validate that end_date >= start_date."""
        if v is not None and info.data.get('start_date') is not None:
            if v < info.data['start_date']:
                raise ValueError('end_date must be greater than or equal to start_date')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Midterm Exam",
                "start_date": "2024-02-01T00:00:00",
                "end_date": "2024-02-20T23:59:59"
            }
        }
    )


class TestResponse(BaseModel):
    """Response schema for test data."""
    id: int
    level_id: int
    name: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "level_id": 1,
                "name": "Midterm Exam",
                "start_date": "2024-02-01T00:00:00",
                "end_date": "2024-02-15T23:59:59",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
    )


# ============================================================================
# QUESTION OPTION SCHEMAS
# ============================================================================

class OptionInput(BaseModel):
    """Schema for question option input."""
    label: str = Field(
        pattern="^[A-J]$",
        description="Option label (A-J)"
    )
    text: str = Field(
        min_length=1,
        max_length=500,
        description="Option text (1-500 characters)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "label": "A",
                "text": "This is the first option"
            }
        }
    )


class OptionResponse(BaseModel):
    """Response schema for question option data."""
    id: int
    question_id: int
    label: str
    text: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "question_id": 1,
                "label": "A",
                "text": "This is the first option",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
    )


# ============================================================================
# QUESTION SCHEMAS
# ============================================================================

class QuestionCreate(BaseModel):
    """Request schema for creating a question."""
    text: str = Field(
        min_length=1,
        max_length=1000,
        description="Question text (1-1000 characters)"
    )
    correct_answer: str = Field(
        pattern="^[A-J]$",
        description="Correct answer label (A-J)"
    )
    options: List[OptionInput] = Field(
        min_length=3,
        max_length=10,
        description="Question options (3-10 options required)"
    )
    
    @field_validator('options')
    @classmethod
    def validate_options(cls, v: List[OptionInput]) -> List[OptionInput]:
        """Validate that options have unique labels and text."""
        labels = set()
        texts = set()
        
        for option in v:
            if option.label in labels:
                raise ValueError(f"Duplicate option label: {option.label}")
            if option.text in texts:
                raise ValueError("Duplicate option text")
            
            labels.add(option.label)
            texts.add(option.text)
        
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "What is 2 + 2?",
                "correct_answer": "A",
                "options": [
                    {"label": "A", "text": "4"},
                    {"label": "B", "text": "5"},
                    {"label": "C", "text": "3"},
                    {"label": "D", "text": "6"}
                ]
            }
        }
    )


class QuestionUpdate(BaseModel):
    """Request schema for updating a question."""
    text: str = Field(
        min_length=1,
        max_length=1000,
        description="Question text (1-1000 characters)"
    )
    correct_answer: str = Field(
        pattern="^[A-J]$",
        description="Correct answer label (A-J)"
    )
    options: List[OptionInput] = Field(
        min_length=3,
        max_length=10,
        description="Question options (3-10 options required)"
    )
    
    @field_validator('options')
    @classmethod
    def validate_options(cls, v: List[OptionInput]) -> List[OptionInput]:
        """Validate that options have unique labels and text."""
        labels = set()
        texts = set()
        
        for option in v:
            if option.label in labels:
                raise ValueError(f"Duplicate option label: {option.label}")
            if option.text in texts:
                raise ValueError("Duplicate option text")
            
            labels.add(option.label)
            texts.add(option.text)
        
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "What is 3 + 3?",
                "correct_answer": "B",
                "options": [
                    {"label": "A", "text": "5"},
                    {"label": "B", "text": "6"},
                    {"label": "C", "text": "7"},
                    {"label": "D", "text": "8"}
                ]
            }
        }
    )


class QuestionResponse(BaseModel):
    """Response schema for question data."""
    id: int
    test_id: int
    text: str
    correct_answer: str
    options: List[OptionResponse]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "test_id": 1,
                "text": "What is 2 + 2?",
                "correct_answer": "A",
                "options": [
                    {"id": 1, "question_id": 1, "label": "A", "text": "4", "created_at": "2024-01-15T10:30:00", "updated_at": "2024-01-15T10:30:00"},
                    {"id": 2, "question_id": 1, "label": "B", "text": "5", "created_at": "2024-01-15T10:30:00", "updated_at": "2024-01-15T10:30:00"},
                    {"id": 3, "question_id": 1, "label": "C", "text": "3", "created_at": "2024-01-15T10:30:00", "updated_at": "2024-01-15T10:30:00"},
                    {"id": 4, "question_id": 1, "label": "D", "text": "6", "created_at": "2024-01-15T10:30:00", "updated_at": "2024-01-15T10:30:00"}
                ],
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
    )


# ============================================================================
# PAGINATION SCHEMAS
# ============================================================================

class PaginatedResponse(BaseModel):
    """Generic paginated response schema."""
    items: List
    total: int = Field(description="Total count of items")
    skip: int = Field(description="Number of items skipped")
    limit: int = Field(description="Maximum items per page")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 100,
                "skip": 0,
                "limit": 50
            }
        }
    )


class SubjectListResponse(BaseModel):
    """Response schema for paginated subject list."""
    items: List[SubjectResponse]
    total: int
    skip: int
    limit: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 10,
                "skip": 0,
                "limit": 50
            }
        }
    )


class LevelListResponse(BaseModel):
    """Response schema for paginated level list."""
    items: List[LevelResponse]
    total: int
    skip: int
    limit: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 5,
                "skip": 0,
                "limit": 50
            }
        }
    )


class TestListResponse(BaseModel):
    """Response schema for paginated test list."""
    items: List[TestResponse]
    total: int
    skip: int
    limit: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 20,
                "skip": 0,
                "limit": 50
            }
        }
    )


class QuestionListResponse(BaseModel):
    """Response schema for paginated question list."""
    items: List[QuestionResponse]
    total: int
    skip: int
    limit: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 50,
                "skip": 0,
                "limit": 100
            }
        }
    )


# ============================================================================
# ERROR RESPONSE SCHEMAS
# ============================================================================

class ErrorResponse(BaseModel):
    """Response schema for error responses."""
    code: str = Field(description="Error code")
    message: str = Field(description="Error message")
    details: Optional[dict] = Field(default=None, description="Additional error details")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "Subject name must be between 1 and 100 characters",
                "details": {"field": "name", "constraint": "length"}
            }
        }
    )
