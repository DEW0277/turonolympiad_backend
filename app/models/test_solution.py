"""TestSolution database model.

This module defines the TestSolution SQLAlchemy model for recording user test submissions.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Index, CheckConstraint, DECIMAL, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TestSolution(Base):
    """TestSolution model for recording user test submissions.
    
    Stores user answers and results for completed tests. Users can submit
    multiple solutions for the same test if they have valid tickets.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        user_id: Foreign key to User, indexed for fast lookups
        test_id: Foreign key to Test, indexed for fast lookups
        solution_data: JSON string containing answers
        score: Optional test score as decimal (5 digits, 2 decimal places), range 0-100
        submitted_at: Timestamp when solution was submitted, indexed
        created_at: Timestamp when record was created
        user: Many-to-one relationship with User model
        test: Many-to-one relationship with Test model
    """
    
    __tablename__ = "test_solutions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    test_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("tests.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    solution_data: Mapped[str] = mapped_column(
        Text, 
        nullable=False
    )
    score: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(5, 2), 
        nullable=True
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="test_solutions", lazy="select")
    test: Mapped["Test"] = relationship("Test", back_populates="test_solutions", lazy="select")
    
    # Constraints and Indexes
    __table_args__ = (
        Index("idx_solution_user_test", "user_id", "test_id"),
        Index("idx_solution_user_submitted", "user_id", "submitted_at"),
        Index("idx_solution_test_submitted", "test_id", "submitted_at"),
        CheckConstraint("score IS NULL OR (score >= 0 AND score <= 100)", name="ck_solution_score_range"),
    )
    
    def __repr__(self) -> str:
        """String representation of TestSolution."""
        return f"<TestSolution(id={getattr(self, 'id', None)}, user_id={getattr(self, 'user_id', None)}, test_id={getattr(self, 'test_id', None)}, score={getattr(self, 'score', None)})>"


# Import User and Test here to avoid circular imports
from app.models.user import User  # noqa: E402, F401
from app.models.test import Test  # noqa: E402, F401
