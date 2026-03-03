"""Test database model.

This module defines the Test SQLAlchemy model for organizing questions into assessments.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Test(Base):
    """Test model for organizing questions into assessments.
    
    Represents a collection of questions organized within a Level, with defined availability dates.
    Tests contain multiple Questions.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        level_id: Foreign key to Level, indexed for fast lookups
        name: Test name (1-100 characters), indexed for fast lookups
        start_date: Optional start date for test availability
        end_date: Optional end date for test availability
        created_at: Timestamp when test was created
        updated_at: Timestamp when test was last updated
        level: Many-to-one relationship with Level model
        questions: One-to-many relationship with Question model (cascade delete)
    """
    
    __tablename__ = "tests"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    level_id: Mapped[int] = mapped_column(Integer, ForeignKey("levels.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    level: Mapped["Level"] = relationship(
        "Level",
        back_populates="tests",
        lazy="select"
    )
    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="test",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("level_id", "name", name="uq_test_level_name"),
        CheckConstraint("end_date IS NULL OR start_date IS NULL OR end_date >= start_date", name="ck_test_date_range"),
        Index("idx_test_level_id", "level_id"),
        Index("idx_test_name", "name"),
        Index("idx_test_dates", "start_date", "end_date"),
        Index("idx_test_level_name", "level_id", "name"),
    )
    
    def __repr__(self) -> str:
        """String representation of Test."""
        return f"<Test(id={getattr(self, 'id', None)}, level_id={getattr(self, 'level_id', None)}, name={getattr(self, 'name', None)})>"


# Import Level and Question here to avoid circular imports
from app.models.level import Level  # noqa: E402, F401
from app.models.question import Question  # noqa: E402, F401
